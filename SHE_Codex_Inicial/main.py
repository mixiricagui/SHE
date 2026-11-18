"""SHE — Interface local de importação, leitura assistida e revisão de atas."""
from __future__ import annotations

import sqlite3
import hashlib
from pathlib import Path

import streamlit as st

from she.banco import (
    confirmar_resultados,
    inicializar,
    listar_alunos,
    listar_atas,
    listar_resultados,
    obter_situacao,
    salvar_aluno,
    salvar_ata,
    salvar_resultados,
)
from she.catalogo import DISCIPLINAS
from she.config import ATAS
from she.validacao import SITUACOES, normalizar_nota
from she.revisao import pendencias_conferencia
from she.importacao import FotoAta, importar_lote
from she.historico import consultar_historico
from she.extracao import LeitorOllama, preparar_rascunho
from she.ata_tabela import inicializar_tabelas, guardar_rascunho, obter_rascunho, importar_revisados, corrigir_cabecalho

st.set_page_config(page_title="SHE | Históricos Escolares", page_icon="📄", layout="wide")
inicializar()
inicializar_tabelas()

st.title("SHE — Sistema de Históricos Escolares")
st.caption("Protótipo local | Não gera documentos oficiais nesta etapa | Conferência humana obrigatória")
st.warning("Use dados fictícios nos testes. Os arquivos e o banco são armazenados localmente, sem criptografia própria nesta versão.")

aba_atas, aba_leitura, aba_alunos, aba_lancamento, aba_conferencia, aba_emissao = st.tabs(
    ["1. Importar ata", "2. Ler ata inteira", "3. Alunos", "4. Lançar notas", "5. Conferir", "6. Emitir histórico"]
)

with aba_atas:
    st.subheader("Importar várias fotografias de atas")
    st.info("Selecione as fotos e confira ano e série de cada uma. Depois abra ‘2. Ler ata inteira’ para extrair os alunos com o leitor local.")
    arquivos = st.file_uploader("Fotografias (JPG, JPEG ou PNG)", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
    fotos = []
    for indice, arquivo in enumerate(arquivos, 1):
        conteudo = arquivo.getvalue()
        chave = hashlib.sha256(conteudo).hexdigest()
        with st.expander(f"Foto {indice} — {arquivo.name}", expanded=len(arquivos) == 1):
            imagem_col, metadados_col = st.columns(2)
            with imagem_col:
                try:
                    st.image(conteudo, use_container_width=True)
                except Exception:
                    st.warning('Não foi possível visualizar esta imagem. A importação validará o arquivo.')
            with metadados_col:
                ano = st.number_input('Ano letivo da foto', min_value=1950, max_value=2100, value=None, step=1, key=f'ano_{indice}_{chave}')
                serie = st.selectbox('Série / ano escolar da foto', (6, 7, 8, 9), index=None, key=f'serie_{indice}_{chave}')
                turma = st.text_input('Turma', key=f'turma_{indice}_{chave}')
                turno = st.selectbox('Turno', ('Não informado', 'Matutino', 'Vespertino', 'Noturno', 'Integral'), key=f'turno_{indice}_{chave}')
                confirmado = st.checkbox('Conferi ano letivo e série no cabeçalho desta foto', key=f'conf_{indice}_{chave}_{ano}_{serie}_{turma}_{turno}')
                fotos.append(FotoAta(conteudo, ano, serie, turma, turno, confirmado))
    if arquivos and st.button('Importar fotos conferidas', type='primary'):
        respostas = importar_lote(fotos)
        for resposta in respostas:
            if resposta['erro']:
                st.warning(f"Foto {resposta['foto']}: {resposta['erro']}")
            else:
                st.success(f"Foto {resposta['foto']}: importada como ata #{resposta['ata_id']}.")
        st.caption('Fotos não confirmadas ou inválidas ficam pendentes. Fotos já importadas não são duplicadas ao tentar novamente.')
    atas_importadas = listar_atas()
    if atas_importadas:
        st.dataframe([{'Ata': a['id'], 'Ano letivo': a['ano_letivo'], 'Série': a['ano_escolar'], 'Turma': a['turma']} for a in atas_importadas], hide_index=True)

with aba_leitura:
    st.subheader('Ler todos os alunos de uma ata')
    st.caption('Leitura local assistida por IA. Revise os nomes, cabeçalhos, notas e situações na foto antes de importar. Nenhuma foto é enviada para serviços externos.')
    atas_leitura = listar_atas()
    if not atas_leitura:
        st.info('Importe uma fotografia na primeira aba.')
    else:
        opcoes_leitura = {f"Ata #{a['id']} — {a['ano_escolar']}º ano / {a['ano_letivo']}": a for a in atas_leitura}
        ata_leitura = opcoes_leitura[st.selectbox('Ata para leitura', list(opcoes_leitura))]
        tid_ocr = ata_leitura['id']
        rascunho = obter_rascunho(tid_ocr)
        st.info('O leitor usa o Ollama neste computador. Consulte docs/LEITURA_LOCAL.md para iniciar o serviço local.')
        modelo_ocr = st.selectbox('Modelo local de visão', ('qwen3.5:0.8b', 'qwen3.5:4b', 'qwen2.5vl:3b'), key=f'modelo_ocr_{tid_ocr}')
        st.caption('O modelo 0.8b é menor e experimental. Confira todas as linhas; funcionar no computador não garante precisão na caligrafia.')
        ativar_leitor = st.checkbox('Ativar leitura local para esta ata', key=f'ativar_leitor_{tid_ocr}')
        substituir = st.checkbox('Substituir o rascunho existente por uma nova leitura', key=f'substituir_{tid_ocr}') if rascunho else False
        if st.button('Ler nomes, notas e situações da foto', disabled=not ativar_leitor or bool(rascunho and not substituir)):
            try:
                with st.spinner('Lendo a ata no computador. Isso pode levar alguns minutos…'):
                    novo_rascunho = LeitorOllama(modelo_ocr).ler(Path(ata_leitura['arquivo']))
                    guardar_rascunho(tid_ocr, novo_rascunho)
                st.session_state[f'versao_ocr_{tid_ocr}'] = st.session_state.get(f'versao_ocr_{tid_ocr}', 0) + 1
                st.rerun()
            except ValueError as exc:
                st.error(str(exc))
            except OSError:
                st.error('A imagem não está acessível. O rascunho anterior foi preservado.')
        if not rascunho and st.button('Preparar tabela para transcrição manual'):
            novo_rascunho = preparar_rascunho({'alunos': [{'nome': '', 'notas': []}]})
            guardar_rascunho(tid_ocr, novo_rascunho)
            st.rerun()
        if rascunho:
            for aviso in rascunho.get('avisos', []):
                st.warning(aviso)
            sugerido_ano, sugerida_serie = rascunho.get('ano_letivo'), rascunho.get('serie')
            st.write(f'Cabeçalho sugerido pelo leitor: ano {sugerido_ano or "não identificado"}, série {sugerida_serie or "não identificada"}.')
            if (sugerido_ano is not None and sugerido_ano != ata_leitura['ano_letivo']) or (sugerida_serie is not None and sugerida_serie != ata_leitura['ano_escolar']):
                st.warning('O cabeçalho lido difere do cadastro da ata. Confira a imagem; as sugestões da IA não alteram o cadastro.')
            with st.expander('Corrigir ano letivo ou série cadastrados'):
                with st.form(f'corrigir_cabecalho_{tid_ocr}'):
                    corrigido_ano = st.number_input('Ano letivo correto', min_value=1950, max_value=2100, value=ata_leitura['ano_letivo'], step=1)
                    corrigida_serie = st.selectbox('Série correta', (6, 7, 8, 9), index=ata_leitura['ano_escolar'] - 6)
                    st.caption('Alterar o cabeçalho exige conferir novamente os resultados já vinculados a esta ata.')
                    if st.form_submit_button('Salvar correção do cabeçalho'):
                        corrigir_cabecalho(tid_ocr, corrigido_ano, corrigida_serie)
                        st.rerun()
            foto_col, tabela_col = st.columns([1, 2])
            with foto_col:
                if Path(ata_leitura['arquivo']).exists():
                    st.image(ata_leitura['arquivo'], use_container_width=True)
            with tabela_col:
                st.caption('Para cada linha, informe um Aluno ID existente OU marque Novo aluno. Preencha linhas que a IA não encontrou. Confira disciplinas em “Não mapeado”, transfira os valores corretos e limpe esse campo após resolver.')
                existentes = listar_alunos()
                if existentes:
                    with st.expander('Consultar IDs dos alunos cadastrados'):
                        st.dataframe([{'ID': a['id'], 'Nome': a['nome'], 'Matrícula': a['matricula'] or ''} for a in existentes], hide_index=True)
                linhas_editor = rascunho['linhas'] or preparar_rascunho({'alunos': [{'nome': '', 'notas': []}]})['linhas']
                revisadas = st.data_editor(linhas_editor, num_rows='dynamic', hide_index=True,
                    key=f"editor_ocr_{tid_ocr}_{st.session_state.get(f'versao_ocr_{tid_ocr}', 0)}",
                    column_config={
                        'Linha': st.column_config.NumberColumn('Linha na foto', min_value=1, step=1, required=True),
                        'Aluno ID': st.column_config.NumberColumn('Aluno ID', min_value=0, step=1),
                        'Importar': st.column_config.CheckboxColumn('Importar', default=False),
                        'Revisado': st.column_config.CheckboxColumn('Revisado na foto', default=False),
                        'Novo aluno': st.column_config.CheckboxColumn('Criar novo aluno', default=False)})
                if st.button('Salvar rascunho da tabela'):
                    guardar_rascunho(tid_ocr, rascunho | {'linhas': revisadas})
                    st.success('Rascunho salvo localmente. Resultados ainda não importados.')
                assinatura = hashlib.sha256(repr(revisadas).encode()).hexdigest()
                confirmou_cabecalho = st.checkbox(f"Conferi na foto: {ata_leitura['ano_escolar']}º ano, ano letivo {ata_leitura['ano_letivo']}, e revisei as linhas selecionadas", key=f'cabecalho_{tid_ocr}_{assinatura}')
                if st.button('Importar alunos e resultados selecionados', disabled=not confirmou_cabecalho):
                    try:
                        ids = importar_revisados(tid_ocr, revisadas, confirmou_cabecalho)
                        for linha in revisadas:
                            linha['Importar'] = False
                            linha['Revisado'] = False
                        guardar_rascunho(tid_ocr, rascunho | {'linhas': revisadas})
                        st.success(f'{len(ids)} aluno(s) importado(s). As notas estão NÃO CONFERIDAS; prossiga para a aba Conferir. Linhas já importadas não serão gravadas novamente.')
                    except (ValueError, sqlite3.Error) as exc:
                        st.error(str(exc) if isinstance(exc, ValueError) else 'Não foi possível gravar. Nenhuma linha deste envio foi importada.')

with aba_alunos:
    st.subheader("Cadastrar estudante")
    with st.form("cadastro_aluno", clear_on_submit=True):
        nome = st.text_input("Nome completo")
        matricula = st.text_input("Matrícula (se disponível)")
        nascimento = st.text_input("Data de nascimento (AAAA-MM-DD; opcional)")
        criar = st.form_submit_button("Cadastrar")
    if criar:
        if len(nome.strip()) < 3:
            st.error("Informe o nome completo.")
        else:
            try:
                ident = salvar_aluno(nome, matricula, nascimento)
                st.success(f"Aluno cadastrado com ID interno {ident}. Verifique homônimos antes de associar resultados.")
            except sqlite3.IntegrityError:
                st.error("A matrícula informada já está cadastrada. Verifique antes de criar outro registro.")
            except ValueError as exc:
                st.error(str(exc))
    cadastrados = listar_alunos()
    if cadastrados:
        st.dataframe([{"ID": a["id"], "Nome": a["nome"], "Matrícula": a["matricula"] or ""} for a in cadastrados], use_container_width=True)

with aba_lancamento:
    st.subheader("Lançamento manual vinculado à ata")
    st.caption("Use a aba Ler ata inteira para extrair sugestões da imagem; esta tela permite corrigir os resultados já vinculados ao aluno.")
    alunos, atas = listar_alunos(), listar_atas()
    if not alunos or not atas:
        st.info("Cadastre pelo menos um aluno e importe uma ata antes de lançar resultados.")
    else:
        aluno_opcoes = {f"#{a['id']} — {a['nome']} (mat. {a['matricula'] or 'não informada'})": a["id"] for a in alunos}
        ata_opcoes = {f"#{a['id']} — {a['ano_escolar']}º ano / {a['ano_letivo']} — {a['turma'] or 'turma não informada'}": a["id"] for a in atas}
        aluno_rotulo = st.selectbox("Estudante", list(aluno_opcoes), key="aluno_lancamento")
        ata_rotulo = st.selectbox("Ata de origem", list(ata_opcoes), key="ata_lancamento")
        aid_l, tid_l = aluno_opcoes[aluno_rotulo], ata_opcoes[ata_rotulo]
        anteriores = {r['disciplina']: r['nota'] for r in listar_resultados(aid_l, tid_l)}
        situacao_anterior = obter_situacao(aid_l, tid_l)
        selecionada_l = next(a for a in atas if a['id'] == tid_l)
        imagem_col, entrada_col = st.columns(2)
        with imagem_col:
            if Path(selecionada_l['arquivo']).exists():
                st.image(selecionada_l['arquivo'], use_container_width=True)
        with entrada_col, st.form(f"notas_{aid_l}_{tid_l}"):
            situacao = st.selectbox("Situação final conforme a ata", SITUACOES, index=SITUACOES.index(situacao_anterior['situacao']) if situacao_anterior else 0)
            observacao = st.text_input("Observação literal (se houver)", value=situacao_anterior['observacao'] if situacao_anterior else '')
            st.markdown("**Notas por disciplina** — deixe em branco apenas se a ata não trouxer a nota.")
            notas_digitadas = {}
            for disciplina in DISCIPLINAS:
                notas_digitadas[disciplina] = st.text_input(disciplina, key=f"nota_{aid_l}_{tid_l}_{disciplina}", value=anteriores.get(disciplina) or '', placeholder="Ex.: 7,5")
            gravar = st.form_submit_button("Gravar para conferência")
        if gravar:
            try:
                notas = {k: normalizar_nota(v) for k, v in notas_digitadas.items()}
                salvar_resultados(aluno_opcoes[aluno_rotulo], ata_opcoes[ata_rotulo], notas, situacao, observacao)
                st.success("Dados armazenados como NÃO CONFERIDOS. Abra a próxima aba.")
            except ValueError as exc:
                st.error(str(exc))

with aba_conferencia:
    st.subheader("Conferência obrigatória")
    alunos, atas = listar_alunos(), listar_atas()
    if not alunos or not atas:
        st.info("Ainda não há alunos e atas para conferir.")
    else:
        aluno_choices = {f"#{a['id']} — {a['nome']}": a["id"] for a in alunos}
        ata_choices = {f"#{a['id']} — {a['ano_escolar']}º ano / {a['ano_letivo']}": a["id"] for a in atas}
        aluno_nome = st.selectbox("Aluno a conferir", list(aluno_choices), key="aluno_conferencia")
        ata_nome = st.selectbox("Ata a conferir", list(ata_choices), key="ata_conferencia")
        aid, tid = aluno_choices[aluno_nome], ata_choices[ata_nome]
        resultados = listar_resultados(aid, tid)
        situacao_reg = obter_situacao(aid, tid)
        if not resultados:
            st.info("Ainda não há resultados lançados para este aluno nesta ata.")
        else:
            selecionada = next(a for a in atas if a["id"] == tid)
            st.write(f"Situação informada: **{situacao_reg['situacao']}**")
            st.dataframe([{"Disciplina": r["disciplina"], "Nota": r["nota"] if r["nota"] is not None else "AUSENTE", "Conferido": bool(r["conferido"])} for r in resultados], use_container_width=True)
            if Path(selecionada["arquivo"]).exists():
                with st.expander("Visualizar fotografia de origem"):
                    st.image(selecionada["arquivo"], use_container_width=True)
            pendencias = pendencias_conferencia(resultados, situacao_reg)
            for pendencia in pendencias:
                st.warning(pendencia)
            versao = hashlib.sha256(('|'.join(str(tuple(r)) for r in resultados) + str(tuple(situacao_reg))).encode()).hexdigest()
            confirmar = st.checkbox("Comparei cuidadosamente todas as informações com a ata original e a situação do estudante.", key=f'conferir_{aid}_{tid}_{versao}')
            if st.button("Marcar resultados como conferidos", disabled=not confirmar or bool(pendencias)):
                try:
                    confirmar_resultados(aid, tid)
                    st.success("Conferência registrada. A emissão ainda dependerá das demais verificações.")
                except ValueError as exc:
                    st.error(str(exc))

with aba_emissao:
    st.subheader("Emissão de histórico escolar")
    alunos_h = listar_alunos()
    if alunos_h:
        opcoes_h = {f"#{a['id']} — {a['nome']}": a['id'] for a in alunos_h}
        escolhido_h = st.selectbox('Histórico consolidado do estudante', list(opcoes_h))
        registros_h, conflitos_h = consultar_historico(opcoes_h[escolhido_h])
        st.caption('As atas são reunidas pelo ID do estudante. Séries sem registro permanecem sem dados; não se presume uma sequência de anos.')
        for serie_h in (6, 7, 8, 9):
            linhas_h = [r for r in registros_h if r['ano_escolar'] == serie_h]
            with st.expander(f'{serie_h}º ano — {len(linhas_h)} lançamento(s)'):
                if linhas_h:
                    st.dataframe(linhas_h, hide_index=True)
                else:
                    st.info('Sem resultados vinculados a esta série.')
        if conflitos_h:
            st.error('Mais de uma ata para a mesma série: ' + ', '.join(map(str, conflitos_h)) + '. É necessário decidir quais registros compõem o histórico; nenhum será sobrescrito automaticamente.')
    st.warning('Emissão oficial bloqueada: faltam homologação do modelo, identificação documental completa e confirmação de escola, matriz curricular e cargas horárias.')
    st.write('O motor XLSX está em desenvolvimento e teste. A cópia do modelo foi preparada para inspeção; ainda não há download de histórico oficial.')
