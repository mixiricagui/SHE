"""Rascunhos persistentes e importação atômica de estudantes revisados da ata."""
import json
from .banco import conexao, momento, registrar_auditoria
from .catalogo import DISCIPLINAS
from .validacao import normalizar_nota, padronizar_texto
from .validacao import validacao_serie


def corrigir_cabecalho(ata_id, ano_letivo, serie):
    validacao_serie(serie)
    if not 1950 <= ano_letivo <= 2100:
        raise ValueError('Ano letivo inválido.')
    with conexao() as conn:
        atual = conn.execute('SELECT ano_letivo,ano_escolar FROM atas WHERE id=?', (ata_id,)).fetchone()
        if not atual:
            raise ValueError('Ata inexistente.')
        if (atual['ano_letivo'], atual['ano_escolar']) != (ano_letivo, serie):
            conn.execute('UPDATE atas SET ano_letivo=?,ano_escolar=? WHERE id=?', (ano_letivo, serie, ata_id))
            conn.execute('UPDATE resultados SET conferido=0,conferido_em=NULL WHERE ata_id=?', (ata_id,))
            registrar_auditoria(conn, 'CABECALHO_ATA_CORRIGIDO', f'ata_id={ata_id}')


def inicializar_tabelas():
    with conexao() as conn:
        conn.executescript('''
            CREATE TABLE IF NOT EXISTS rascunhos_atas (
                ata_id INTEGER PRIMARY KEY REFERENCES atas(id), conteudo TEXT NOT NULL,
                atualizado_em TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS linhas_importadas (
                ata_id INTEGER NOT NULL REFERENCES atas(id), linha INTEGER NOT NULL,
                aluno_id INTEGER NOT NULL REFERENCES alunos(id), referencia TEXT NOT NULL,
                situacao_literal TEXT NOT NULL, PRIMARY KEY(ata_id,linha));
        ''')


def guardar_rascunho(ata_id, rascunho):
    with conexao() as conn:
        conn.execute('''INSERT INTO rascunhos_atas VALUES(?,?,?) ON CONFLICT(ata_id)
            DO UPDATE SET conteudo=excluded.conteudo, atualizado_em=excluded.atualizado_em''',
            (ata_id, json.dumps(rascunho, ensure_ascii=False), momento()))
        registrar_auditoria(conn, 'RASCUNHO_ATA_SALVO', f'ata_id={ata_id}')


def obter_rascunho(ata_id):
    with conexao() as conn:
        r = conn.execute('SELECT conteudo FROM rascunhos_atas WHERE ata_id=?', (ata_id,)).fetchone()
        return json.loads(r['conteudo']) if r else None


def importar_revisados(ata_id, linhas, metadados_confirmados=False):
    if not metadados_confirmados:
        raise ValueError('Confira o ano letivo e a série desta ata antes de salvar.')
    selecionadas = [r for r in linhas if r.get('Importar') is True]
    if not selecionadas:
        raise ValueError('Selecione pelo menos uma linha para importar.')
    preparados = []
    numeros = set()
    for r in selecionadas:
        numero = r.get('Linha')
        if type(numero) is not int or numero < 1 or numero in numeros:
            raise ValueError('Cada estudante precisa ter um número de linha único e positivo.')
        numeros.add(numero)
        if r.get('Revisado') is not True or len(str(r.get('Nome', '')).strip()) < 3:
            raise ValueError(f'Linha {numero}: confira o nome e marque Revisado.')
        if str(r.get('Não mapeado', '')).strip():
            raise ValueError(f'Linha {numero}: resolva os componentes não mapeados antes de importar.')
        novo = r.get('Novo aluno') is True
        aid = r.get('Aluno ID') or 0
        if type(aid) is not int or aid < 0 or novo == bool(aid):
            raise ValueError(f'Linha {numero}: escolha um ID existente OU marque Novo aluno.')
        notas = {d: normalizar_nota('' if r.get(d) is None else str(r[d])) for d in DISCIPLINAS}
        literal = str(r.get('Situação literal') or '').strip()
        situacao = {'aprovado': 'APROVADO', 'aprovada': 'APROVADO', 'reprovado': 'REPROVADO',
                    'reprovada': 'REPROVADO', 'transferido': 'TRANSFERIDO', 'transferida': 'TRANSFERIDA'}.get(padronizar_texto(literal), 'OUTRO' if literal else 'PENDENTE')
        preparados.append((r, numero, novo, aid, notas, literal, situacao))
    ids = []
    with conexao() as conn:
        if not conn.execute('SELECT id FROM atas WHERE id=?', (ata_id,)).fetchone():
            raise ValueError('Ata inexistente.')
        for r, numero, novo, aid, notas, literal, situacao in preparados:
            if conn.execute('SELECT 1 FROM linhas_importadas WHERE ata_id=? AND linha=?', (ata_id, numero)).fetchone():
                raise ValueError(f'Linha {numero} já importada. Corrija os dados na tela de lançamento.')
            if novo:
                aid = conn.execute('INSERT INTO alunos(nome,criado_em) VALUES(?,?)', (r['Nome'].strip(), momento())).lastrowid
            elif not conn.execute('SELECT 1 FROM alunos WHERE id=?', (aid,)).fetchone():
                raise ValueError(f'Linha {numero}: ID de aluno inexistente.')
            if aid in ids or conn.execute('SELECT 1 FROM resultados WHERE ata_id=? AND aluno_id=?', (ata_id, aid)).fetchone():
                raise ValueError(f'Linha {numero}: aluno já possui resultados nesta ata; nenhuma alteração foi salva.')
            ids.append(aid)
            conn.execute('INSERT INTO situacoes VALUES(?,?,?,?)', (aid, ata_id, situacao, str(r.get('Observação') or '')))
            conn.executemany('INSERT INTO resultados(aluno_id,ata_id,disciplina,nota) VALUES(?,?,?,?)',
                             [(aid, ata_id, d, n) for d, n in notas.items()])
            conn.execute('INSERT INTO linhas_importadas VALUES(?,?,?,?,?)', (ata_id, numero, aid, str(r.get('Referência') or f'Linha {numero}'), literal))
            registrar_auditoria(conn, 'LINHA_ATA_IMPORTADA', f'ata_id={ata_id},linha={numero},aluno_id={aid}')
    return ids
