from io import BytesIO
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from PIL import Image
from she import banco, importacao
from she.historico import consultar_historico


def imagem(cor):
    buffer = BytesIO()
    Image.new('RGB', (500, 500), cor).save(buffer, format='PNG')
    return buffer.getvalue()


class TestLote(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        raiz = Path(self.temp.name)
        self.raiz = raiz
        for alvo, nome, valor in ((banco, 'BANCO', raiz / 'teste.db'), (importacao, 'ATAS', raiz)):
            p = patch.object(alvo, nome, valor)
            p.start()
            self.addCleanup(p.stop)
        banco.inicializar()

    def foto(self, cor='white', ano=2024, serie=8, confirmado=True):
        return importacao.FotoAta(imagem(cor), ano, serie, confirmado=confirmado)

    def test_lote_anos_distintos(self):
        resultado = importacao.importar_lote([self.foto(), self.foto('blue', 2025, 9)])
        self.assertTrue(all(r['ata_id'] for r in resultado))
        atas = banco.listar_atas()
        self.assertEqual({(a['ano_letivo'], a['ano_escolar']) for a in atas}, {(2024, 8), (2025, 9)})

    def test_reenvio_nao_duplica(self):
        foto = self.foto()
        respostas = importacao.importar_lote([foto, foto])
        self.assertIsNotNone(respostas[0]['ata_id'])
        self.assertIn('já foi importada', respostas[1]['erro'])
        self.assertEqual(len(list(self.raiz.glob('*.png'))), 1)

    def test_falha_parcial_e_confirmacao(self):
        respostas = importacao.importar_lote([self.foto(confirmado=False), importacao.FotoAta(b'invalida', 2025, 9, confirmado=True), self.foto('blue')])
        self.assertEqual([bool(r['erro']) for r in respostas], [True, True, False])
        self.assertEqual(len(banco.listar_atas()), 1)

    def test_metadados_ausentes(self):
        respostas = importacao.importar_lote([self.foto(ano=None), self.foto(serie=None)])
        self.assertTrue(all(r['erro'] for r in respostas))
        self.assertEqual(banco.listar_atas(), [])

    def test_consolidacao_por_id_e_conflito(self):
        aluno = banco.salvar_aluno('Estudante Sintético')
        homonimo = banco.salvar_aluno('Estudante Sintético')
        respostas = importacao.importar_lote([self.foto(), self.foto('blue', 2025, 9), self.foto('red', 2023, 8)])
        for resposta in respostas:
            banco.salvar_resultados(aluno, resposta['ata_id'], {'Matemática': '7,5'}, 'APROVADO', '')
        registros, conflitos = consultar_historico(aluno)
        self.assertEqual(len(registros), 3)
        self.assertEqual(conflitos, [8])
        self.assertEqual(consultar_historico(homonimo), ([], []))
