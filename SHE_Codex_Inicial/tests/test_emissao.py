from copy import deepcopy
from dataclasses import replace
from hashlib import sha256
from io import BytesIO
from pathlib import Path
import tempfile
import unittest
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font
from she.catalogo import DISCIPLINAS
from she.emissao import AnoHistorico, DadosHistorico, gerar_xlsx


class TestEmissao(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.modelo = Path(self.temp.name) / 'sintetico.xlsx'
        w = Workbook()
        f = w.active
        f.title = 'E_Fundamental'
        v = w.create_sheet('E_Fund_Verso')
        f.merge_cells('H14:W14')
        f['H14'] = 'Exemplo sintético anterior'
        f['X29'].font = Font(bold=True)
        f['A1'] = 'Cabeçalho sintético'
        f['AB54'] = '=SUM(Y29:Y48)'
        f.print_area = 'A1:AD60'
        for row in f['J26:AA54']:
            for c in row:
                c.value = 9
        for row in v['C3:O11']:
            for c in row:
                c.value = 'ANTERIOR SINTÉTICO'
        w.save(self.modelo)
        w.close()
        self.original = self.modelo.read_bytes()
        self.mapa = {
            'aprovado': True, 'sha256': sha256(self.original).hexdigest(),
            'identificacao': {'nome': 'H14', 'matricula': 'AA14'},
            'limpar': {'E_Fundamental': ['H14:W14', 'AA14:AA14', 'J26:AA54'], 'E_Fund_Verso': ['C3:O11']},
        }
        self.ano8 = AnoHistorico(8, 2024, dict.fromkeys(DISCIPLINAS, '7,5'), dict.fromkeys(DISCIPLINAS, '80'), 'Escola Fictícia', 'Município Fictício', 'BA', True, True)
        self.ano9 = replace(self.ano8, serie=9, ano_letivo=2025, notas=dict.fromkeys(DISCIPLINAS, '8'))
        self.dados = DadosHistorico(1, {'nome': 'Estudante Fictício', 'matricula': 'TESTE-01'}, [self.ano8, self.ano9], True, True, True)

    def gerar(self, dados=None, mapa=None):
        return load_workbook(BytesIO(gerar_xlsx(self.modelo, dados or self.dados, mapa or self.mapa)))

    def test_colunas_trajetoria_limpeza_e_layout(self):
        w = self.gerar()
        self.addCleanup(w.close)
        f, v = w.worksheets
        self.assertEqual((f['X29'].value, f['Z29'].value), (7.5, 8))
        self.assertEqual((f['Y29'].value, f['AA29'].value), (80, 80))
        self.assertIsNone(f['T29'].value)
        self.assertIsNone(f['J28'].value)
        self.assertIsNone(v['C3'].value)
        self.assertIsNone(v['E9'].value)
        self.assertEqual((v['C10'].value, v['C11'].value), (2024, 2025))
        self.assertEqual(v['E10'].value, 'Escola Fictícia')
        self.assertIn('H14:W14', str(f.merged_cells))
        self.assertTrue(f['X29'].font.bold)
        self.assertEqual(f['AB54'].value, '=SUM(Y29:Y48)')
        self.assertIn('$A$1:$AD$60', str(f.print_area))
        self.assertEqual(self.original, self.modelo.read_bytes())

    def test_ano_nao_pertencente_nao_herda(self):
        w = self.gerar(replace(self.dados, anos=[self.ano8]))
        self.addCleanup(w.close)
        self.assertIsNone(w['E_Fundamental']['Z29'].value)
        self.assertIsNone(w['E_Fund_Verso']['C11'].value)

    def test_bloqueios(self):
        casos = [replace(self.dados, identificacao_conferida=False), replace(self.dados, identificacao={'nome': 'Fictício'}), replace(self.dados, anos=[replace(self.ano8, conferido=False)]), replace(self.dados, anos=[replace(self.ano8, carga_confirmada=False)]), replace(self.dados, anos=[self.ano8, self.ano8]), replace(self.dados, escola_confirmada=False), replace(self.dados, escala_confirmada=False)]
        for caso in casos:
            with self.subTest(caso=caso.aluno_id), self.assertRaises(ValueError):
                gerar_xlsx(self.modelo, caso, self.mapa)

    def test_modelo_sem_aprovacao_ou_alterado(self):
        for mudanca in ({'aprovado': False}, {'sha256': 'diferente'}):
            with self.assertRaises(ValueError):
                gerar_xlsx(self.modelo, self.dados, self.mapa | mudanca)

    def test_celula_fora_mapa_e_formula_como_texto(self):
        mapa = deepcopy(self.mapa)
        mapa['identificacao']['nome'] = 'A1'
        with self.assertRaises(ValueError):
            gerar_xlsx(self.modelo, self.dados, mapa)
        dados = replace(self.dados, identificacao={'nome': '=1+1', 'matricula': 'TESTE'})
        w = self.gerar(dados)
        self.addCleanup(w.close)
        self.assertEqual(w['E_Fundamental']['H14'].data_type, 's')
