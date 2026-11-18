import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from she import banco
from she.catalogo import DISCIPLINAS


class TestFluxo(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.raiz = Path(self.temp.name)
        self.patch = patch.object(banco, 'BANCO', self.raiz / 'teste.sqlite3')
        self.patch.start()
        self.addCleanup(self.patch.stop)
        banco.inicializar()
        self.aluno = banco.salvar_aluno('Estudante Fictício')
        self.foto = self.raiz / 'foto.png'
        self.foto.write_bytes(b'imagem sintetica')
        self.ata = banco.salvar_ata(self.foto, 2024, 8, 'A', 'Matutino')

    def salvar(self, notas=None, situacao='APROVADO'):
        banco.salvar_resultados(self.aluno, self.ata, notas if notas is not None else dict.fromkeys(DISCIPLINAS, '7,5'), situacao, '')

    def test_conferencia_e_edicao(self):
        self.salvar()
        banco.confirmar_resultados(self.aluno, self.ata)
        self.assertTrue(all(r['conferido'] for r in banco.listar_resultados(self.aluno, self.ata)))
        self.salvar({'Matemática': '0'})
        registros = banco.listar_resultados(self.aluno, self.ata)
        self.assertFalse(any(r['conferido'] for r in registros))
        self.assertEqual(next(r['nota'] for r in registros if r['disciplina'] == 'Matemática'), '0')

    def test_ausencia_bloqueia(self):
        self.salvar({'Matemática': None})
        with self.assertRaises(ValueError):
            banco.confirmar_resultados(self.aluno, self.ata)

    def test_sem_resultados_bloqueia(self):
        with self.assertRaises(ValueError):
            banco.confirmar_resultados(self.aluno, self.ata)

    def test_homonimos(self):
        outro = banco.salvar_aluno('Estudante Fictício')
        self.salvar()
        self.assertNotEqual(outro, self.aluno)
        self.assertEqual(banco.listar_resultados(outro, self.ata), [])

    def test_duplicata(self):
        with self.assertRaisesRegex(ValueError, 'já foi importada'):
            banco.salvar_ata(self.foto, 2024, 8, 'A', 'Matutino')
        self.assertEqual(len(banco.listar_atas()), 1)

    def test_ordem_e_rotulos(self):
        self.salvar({'Matematica': '7,5', 'Português': '8'})
        antes = [tuple(r) for r in banco.listar_resultados(self.aluno, self.ata)]
        self.salvar({'Língua Portuguesa': '8', 'Matemática': '7.5'})
        self.assertEqual(antes, [tuple(r) for r in banco.listar_resultados(self.aluno, self.ata)])

    def test_ilegivel_e_transferencia_nao_sao_notas(self):
        for valor in ('ilegível', 'TRANSFERIDO', 'TRANSFERIDA', 'NaN'):
            with self.assertRaises(ValueError):
                self.salvar({'Matemática': valor})
        self.assertEqual(banco.listar_resultados(self.aluno, self.ata), [])

    def test_situacoes_especiais(self):
        for situacao in ('PENDENTE', 'TRANSFERIDO', 'TRANSFERIDA', 'OUTRO'):
            self.salvar(situacao=situacao)
            with self.assertRaises(ValueError):
                banco.confirmar_resultados(self.aluno, self.ata)

    def test_nascimento_invalido(self):
        with self.assertRaises(ValueError):
            banco.salvar_aluno('Outro Fictício', nascimento='2024-02-30')

    def test_migracao_idempotente(self):
        banco.inicializar()
        banco.inicializar()
        self.assertEqual(len(banco.listar_atas()), 1)
