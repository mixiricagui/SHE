from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from streamlit.testing.v1 import AppTest
from she import banco
from she.ata_tabela import inicializar_tabelas, guardar_rascunho
from she.extracao import preparar_rascunho


class TestInterface(unittest.TestCase):
    def test_inicio_e_historico_consolidado(self):
        with tempfile.TemporaryDirectory() as pasta:
            with patch.object(banco, 'BANCO', Path(pasta) / 'interface.db'):
                banco.inicializar()
                aluno = banco.salvar_aluno('Estudante Fictício')
                origem = Path(pasta) / 'origem.png'
                origem.write_bytes(b'ficticio')
                ata = banco.salvar_ata(origem, 2024, 8, 'A', 'Matutino')
                origem.unlink()  # Sem fotografia na tela; fixture é apenas metadado.
                banco.salvar_resultados(aluno, ata, {'Matemática': '7,5'}, 'APROVADO', '')
                inicializar_tabelas()
                rascunho = preparar_rascunho({'alunos': [{'nome': 'Outro Estudante Fictício', 'situacao': 'Aprovado', 'notas': [{'disciplina': 'Matemática', 'valor': '8'}]}]})
                rascunho['linhas'][0].update({'Importar': True, 'Revisado': True, 'Novo aluno': True})
                guardar_rascunho(ata, rascunho)
                app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / 'main.py')).run(timeout=60)
                self.assertFalse(app.exception)
                self.assertTrue(any('várias fotografias' in s.value for s in app.subheader))
                self.assertTrue(any(s.label == 'Histórico consolidado do estudante' for s in app.selectbox))
                self.assertTrue(any(s.value == 'Ler todos os alunos de uma ata' for s in app.subheader))
                confirmacao = next(c for c in app.checkbox if c.label.startswith('Conferi na foto:'))
                confirmacao.check().run()
                next(b for b in app.button if b.label == 'Importar alunos e resultados selecionados').click().run()
                self.assertFalse(app.exception)
                self.assertEqual(len(banco.listar_alunos()), 2)
