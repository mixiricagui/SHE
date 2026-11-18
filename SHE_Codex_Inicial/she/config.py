"""Configuração local. Nunca salvar dados de alunos no repositório Git."""
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DADOS = RAIZ / "dados"
ATAS = DADOS / "atas"
REFERENCIAS = DADOS / "referencias"
MODELOS = RAIZ / "modelos"
EXPORTACOES = RAIZ / "exports"
BANCO = DADOS / "she.sqlite3"


def preparar_pastas() -> None:
    for pasta in (DADOS, ATAS, REFERENCIAS, MODELOS, EXPORTACOES):
        pasta.mkdir(parents=True, exist_ok=True)
