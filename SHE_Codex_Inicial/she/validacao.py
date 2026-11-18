"""Validações sem inventar notas e sem equiparar vazio a zero."""
from decimal import Decimal, InvalidOperation
import unicodedata

SITUACOES = ("PENDENTE", "APROVADO", "REPROVADO", "TRANSFERIDO", "TRANSFERIDA", "OUTRO")


def normalizar_nota(entrada: str) -> str | None:
    """Retorna texto decimal canônico 0..10, ou None se vazio.

    A escala 0..10 deve ser confirmada pela escola antes da produção.
    """
    s = str(entrada).strip()
    if not s:
        return None
    if s.count(",") + s.count(".") > 1:
        raise ValueError("Formato de nota inválido: use 7,5 ou 7.5.")
    try:
        nota = Decimal(s.replace(",", "."))
    except InvalidOperation as exc:
        raise ValueError("Nota não numérica: confira a ata.") from exc
    if not nota.is_finite() or nota < 0 or nota > 10:
        raise ValueError("Nota fora da faixa 0 a 10; verifique a escala da escola.")
    return str(nota)


def padronizar_texto(valor: str) -> str:
    s = unicodedata.normalize("NFKD", valor.strip().lower())
    return "".join(ch for ch in s if not unicodedata.combining(ch))


def validacao_serie(serie: int) -> None:
    if serie not in (6, 7, 8, 9):
        raise ValueError("Protótipo inicial: somente 6º a 9º ano.")
