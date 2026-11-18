"""Importação local em lote, com resultado independente para cada fotografia."""
from dataclasses import dataclass
from io import BytesIO
from uuid import uuid4
import sqlite3

from PIL import Image, ImageOps, UnidentifiedImageError

from . import banco
from .config import ATAS, preparar_pastas
from .validacao import validacao_serie


@dataclass(frozen=True)
class FotoAta:
    conteudo: bytes
    ano_letivo: int | None
    ano_escolar: int | None
    turma: str = ''
    turno: str = 'Não informado'
    confirmado: bool = False


def importar_lote(fotos: list[FotoAta]) -> list[dict]:
    preparar_pastas()
    respostas = []
    for indice, foto in enumerate(fotos, 1):
        caminho = None
        try:
            if not foto.confirmado:
                raise ValueError('Confirme ano letivo e série na fotografia.')
            validacao_serie(foto.ano_escolar)
            if foto.ano_letivo is None or not 1950 <= foto.ano_letivo <= 2100:
                raise ValueError('Informe o ano letivo desta fotografia.')
            with Image.open(BytesIO(foto.conteudo)) as original:
                imagem = ImageOps.exif_transpose(original).convert('RGB')
                if min(imagem.size) < 400:
                    raise ValueError('Fotografia pequena demais; use uma imagem mais nítida.')
                caminho = ATAS / f'{uuid4().hex}.png'
                imagem.save(caminho, format='PNG')
            ata_id = banco.salvar_ata(caminho, foto.ano_letivo, foto.ano_escolar, foto.turma, foto.turno)
            respostas.append({'foto': indice, 'ata_id': ata_id, 'erro': None})
        except (ValueError, OSError, UnidentifiedImageError, Image.DecompressionBombError, sqlite3.Error) as exc:
            if caminho is not None:
                caminho.unlink(missing_ok=True)
            mensagem = str(exc) if isinstance(exc, ValueError) else 'Arquivo inválido ou indisponível; confira a fotografia.'
            respostas.append({'foto': indice, 'ata_id': None, 'erro': mensagem})
    return respostas
