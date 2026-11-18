import json
from pathlib import Path
import tempfile
import unittest
from io import BytesIO
from urllib.error import HTTPError
from unittest.mock import MagicMock, patch
from she.extracao import LeitorOllama, preparar_rascunho, SemRedirecionamento


def resposta_ficticia():
    return {'ano_letivo': 2024, 'serie': 8, 'alunos': [
        {'nome': 'Estudante Fictício A', 'situacao': 'Aprovado', 'notas': [
            {'disciplina': 'Matemática', 'valor': '0'}, {'disciplina': 'Português', 'valor': '7,5'}]},
        {'nome': 'Estudante Fictício B', 'situacao': 'TRANSFERIDA', 'notas': [
            {'disciplina': 'Português', 'valor': None}, {'disciplina': 'Matemática', 'valor': None}]}]}


class TestExtracao(unittest.TestCase):
    def test_erro_de_memoria_explica_limite(self):
        with tempfile.TemporaryDirectory() as pasta:
            foto = Path(pasta) / 'ficticia.png'
            foto.write_bytes(b'imagem sintetica')
            erro = HTTPError('http://127.0.0.1:11434/api/chat', 500, 'error', {}, BytesIO(b'{"error":"model requires more system memory"}'))
            with patch('she.extracao.urllib.request.build_opener') as criar:
                criar.return_value.open.side_effect = erro
                with self.assertRaisesRegex(ValueError, 'falta memória'):
                    LeitorOllama().ler(foto)

    def test_todos_alunos_e_rotulos(self):
        r = preparar_rascunho(resposta_ficticia())
        self.assertEqual(len(r['linhas']), 2)
        self.assertEqual(r['linhas'][0]['Matemática'], '0')
        self.assertEqual(r['linhas'][0]['Língua Portuguesa'], '7,5')
        self.assertEqual(r['linhas'][1]['Matemática'], '')
        self.assertEqual(r['linhas'][1]['Situação literal'], 'TRANSFERIDA')
        self.assertFalse(any(x['Revisado'] or x['Importar'] or x['Novo aluno'] for x in r['linhas']))

    def test_disciplina_desconhecida_e_duplicada_preservadas(self):
        r = resposta_ficticia()
        r['alunos'][0]['notas'] += [{'disciplina': 'MAT desconhecida', 'valor': '9'}, {'disciplina': 'Matemática', 'valor': '6'}]
        linha = preparar_rascunho(r)['linhas'][0]
        self.assertIn('MAT desconhecida: 9', linha['Não mapeado'])
        self.assertIn('Matemática: 6', linha['Não mapeado'])
        self.assertEqual(linha['Matemática'], '0')

    def test_resposta_invalida_e_vazia(self):
        for r in ([], {}, {'alunos': [{}]}):
            with self.assertRaises(ValueError):
                preparar_rascunho(r)
        self.assertTrue(preparar_rascunho({'alunos': []})['avisos'])

    def test_modelos_cloud_e_redirecionamentos_bloqueados(self):
        self.assertEqual(LeitorOllama('qwen3.5:0.8b').modelo, 'qwen3.5:0.8b')
        self.assertEqual(LeitorOllama('qwen3.5:4b').modelo, 'qwen3.5:4b')
        with self.assertRaises(ValueError):
            LeitorOllama('modelo:cloud')
        self.assertIsNone(SemRedirecionamento().redirect_request(None, None, 302, '', {}, 'https://externo.invalid'))

    def test_contrato_http_local_simulado(self):
        with tempfile.TemporaryDirectory() as pasta:
            foto = Path(pasta) / 'ficticia.png'
            foto.write_bytes(b'imagem sintetica')
            resposta = MagicMock()
            resposta.__enter__.return_value.read.return_value = json.dumps({'done': True, 'message': {'content': json.dumps(resposta_ficticia())}}).encode()
            with patch('she.extracao.urllib.request.build_opener') as criar:
                criar.return_value.open.return_value = resposta
                r = LeitorOllama().ler(foto)
                pedido = criar.return_value.open.call_args.args[0]
                self.assertEqual(pedido.full_url, 'http://127.0.0.1:11434/api/chat')
                corpo = json.loads(pedido.data)
                self.assertTrue(corpo['messages'][0]['images'])
                self.assertEqual(corpo['model'], 'qwen2.5vl:3b')
                self.assertEqual(len(r['linhas']), 2)
                resposta.__enter__.return_value.read.return_value = b'{"done":false}'
                with self.assertRaises(ValueError):
                    LeitorOllama().ler(foto)
