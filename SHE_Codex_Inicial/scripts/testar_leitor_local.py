"""Teste real opcional com imagem sintética. Não usa dados do banco escolar."""
import json
import sys
import time
import argparse
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
from she.extracao import LeitorOllama

pasta = RAIZ / 'dados' / 'teste_leitor'
pasta.mkdir(parents=True, exist_ok=True)
imagem = Image.new('RGB', (1200, 360), 'white')
desenho = ImageDraw.Draw(imagem)
fonte = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 28)
for y, texto in [(20, 'ATA FICTICIA - ANO LETIVO 2024 - 8o ANO'),
                 (90, 'NOME                         MATEMATICA    PORTUGUES    SITUACAO'),
                 (160, 'ALUNO TESTE ALFA        7,5                     8,0                APROVADO'),
                 (230, 'ALUNO TESTE BETA        6,0                     7,0                APROVADO')]:
    desenho.text((25, y), texto, fill='black', font=fonte)
foto = pasta / 'ata_sintetica.png'
imagem.save(foto)
inicio = time.monotonic()
parser = argparse.ArgumentParser()
parser.add_argument('--modelo', default='qwen3.5:0.8b', choices=['qwen3.5:0.8b', 'qwen3.5:4b', 'qwen2.5vl:3b'])
args = parser.parse_args()
try:
    rascunho = LeitorOllama(args.modelo).ler(foto)
    resumo = {'status': 'respondeu', 'segundos': round(time.monotonic() - inicio, 1),
              'alunos_encontrados': len(rascunho['linhas']),
              'ano_letivo': rascunho['ano_letivo'], 'serie': rascunho['serie']}
    (pasta / 'resultado_sintetico.json').write_text(json.dumps(rascunho, ensure_ascii=False, indent=2), encoding='utf-8')
except ValueError as exc:
    resumo = {'status': 'falhou', 'segundos': round(time.monotonic() - inicio, 1), 'motivo': str(exc)}
resumo['modelo'] = args.modelo
(pasta / 'diagnostico.json').write_text(json.dumps(resumo, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(resumo, ensure_ascii=False))
sys.exit(0 if resumo['status'] == 'respondeu' else 1)
