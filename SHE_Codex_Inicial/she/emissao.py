"""Motor XLSX com mapa versionado; produção depende de homologação."""
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from hashlib import sha256
from io import BytesIO
from pathlib import Path
import json
from openpyxl import load_workbook
from openpyxl.cell.cell import MergedCell
from .catalogo import DISCIPLINAS, COLUNAS_POR_ANO, COLUNAS_CARGA_HORARIA, LINHAS_MODELO
from .validacao import normalizar_nota, validacao_serie


@dataclass(frozen=True)
class AnoHistorico:
    serie: int
    ano_letivo: int
    notas: dict[str, str]
    cargas: dict[str, str]
    escola: str
    municipio: str
    uf: str
    conferido: bool = False
    carga_confirmada: bool = False


@dataclass(frozen=True)
class DadosHistorico:
    aluno_id: int
    identificacao: dict[str, str]
    anos: list[AnoHistorico]
    identificacao_conferida: bool = False
    escola_confirmada: bool = False
    escala_confirmada: bool = False


def carregar_mapa(caminho: Path) -> dict:
    return json.loads(caminho.read_text(encoding='utf-8'))


def gerar_xlsx(modelo: Path, dados: DadosHistorico, mapa: dict) -> bytes:
    """Motor puro. O chamador deve fornecer a revisão mais recente do banco.

    Não identifica alunos por nome nem escolhe entre atas conflitantes.
    O mapa homologado deve cobrir TODOS os dados variáveis do exemplar.
    """
    conteudo = modelo.read_bytes()
    if mapa.get('aprovado') is not True or mapa.get('sha256') != sha256(conteudo).hexdigest():
        raise ValueError('Modelo não homologado ou arquivo diferente do modelo conferido.')
    if not all((dados.identificacao_conferida, dados.escola_confirmada, dados.escala_confirmada)):
        raise ValueError('Confirme identificação, estabelecimento e escala de notas.')
    if dados.aluno_id <= 0 or not dados.anos:
        raise ValueError('Aluno ou trajetória escolar ausente.')
    campos = mapa.get('identificacao', {})
    if not campos or any(not dados.identificacao.get(campo, '').strip() for campo in campos):
        raise ValueError('Identificação obrigatória incompleta.')
    series = set()
    for ano in dados.anos:
        validacao_serie(ano.serie)
        if ano.serie in series:
            raise ValueError('Mais de um registro para a mesma série: resolva o conflito.')
        series.add(ano.serie)
        if not 1950 <= ano.ano_letivo <= 2100:
            raise ValueError('Ano letivo inválido.')
        if not ano.conferido or not ano.carga_confirmada:
            raise ValueError('Notas ou carga horária ainda não conferidas.')
        if not all(x.strip() for x in (ano.escola, ano.municipio, ano.uf)) or len(ano.uf.strip()) != 2:
            raise ValueError('Trajetória escolar incompleta.')
        if set(ano.notas) != set(DISCIPLINAS) or set(ano.cargas) != set(DISCIPLINAS):
            raise ValueError('Componentes curriculares incompletos ou não mapeados.')
        for disciplina in DISCIPLINAS:
            if ano.notas[disciplina] is None or normalizar_nota(ano.notas[disciplina]) is None:
                raise ValueError('Nota ausente.')
            try:
                carga = Decimal(str(ano.cargas[disciplina]).replace(',', '.'))
            except InvalidOperation as exc:
                raise ValueError('Carga horária inválida.') from exc
            if not carga.is_finite() or carga <= 0:
                raise ValueError('Carga horária inválida.')
    livro = load_workbook(BytesIO(conteudo))
    try:
        frente = livro['E_Fundamental']
        verso = livro['E_Fund_Verso']
        permitidas = set()
        for aba, intervalos in mapa['limpar'].items():
            for intervalo in intervalos:
                for linha in livro[aba][intervalo]:
                    for celula in linha:
                        if isinstance(celula, MergedCell):
                            continue
                        permitidas.add((aba, celula.coordinate))
                        if celula.data_type != 'f':
                            celula.value = None

        def preencher(aba, endereco, valor):
            celula = aba[endereco]
            if (aba.title, endereco) not in permitidas or isinstance(celula, MergedCell) or celula.data_type == 'f':
                raise ValueError(f'Célula de destino não autorizada: {aba.title}!{endereco}')
            celula.value = valor
            if isinstance(valor, str):
                celula.data_type = 's'

        for campo, endereco in campos.items():
            preencher(frente, endereco, dados.identificacao[campo])
        for ano in dados.anos:
            for disciplina, linha in LINHAS_MODELO.items():
                preencher(frente, f'{COLUNAS_POR_ANO[ano.serie]}{linha}', Decimal(normalizar_nota(ano.notas[disciplina])))
                preencher(frente, f'{COLUNAS_CARGA_HORARIA[ano.serie]}{linha}', Decimal(str(ano.cargas[disciplina]).replace(',', '.')))
            linha_verso = ano.serie + 2
            for coluna, valor in (('C', ano.ano_letivo), ('E', ano.escola), ('M', ano.municipio), ('O', ano.uf)):
                preencher(verso, f'{coluna}{linha_verso}', valor)
        saida = BytesIO()
        livro.save(saida)
        return saida.getvalue()
    finally:
        livro.close()


def emitir_historico(aluno_id: int, caminho_modelo: Path, destino: Path) -> Path:
    raise ValueError('Emissão oficial bloqueada: homologação do modelo e cadastro documental ainda pendentes.')
