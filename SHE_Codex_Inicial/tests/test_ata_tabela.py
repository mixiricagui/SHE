from copy import deepcopy
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from she import banco
from she.ata_tabela import inicializar_tabelas, guardar_rascunho, obter_rascunho, importar_revisados, corrigir_cabecalho
from she.extracao import preparar_rascunho
from she.catalogo import DISCIPLINAS


class TestTabelaAta(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        raiz = Path(self.temp.name)
        p = patch.object(banco, 'BANCO', raiz / 'teste.db')
        p.start()
        self.addCleanup(p.stop)
        banco.inicializar()
        inicializar_tabelas()
        foto = raiz / 'foto.png'
        foto.write_bytes(b'sintetica')
        self.ata = banco.salvar_ata(foto, 2024, 8, 'A', 'Matutino')
        self.rascunho = preparar_rascunho({'alunos': [
            {'nome': 'Estudante Fictício', 'situacao': 'Aprovado', 'notas': [{'disciplina': d, 'valor': '7,5'} for d in DISCIPLINAS]},
            {'nome': 'Estudante Fictício', 'situacao': 'Transferida', 'notas': []}]})
        self.linhas = self.rascunho['linhas']
        for r in self.linhas:
            r.update({'Importar': True, 'Revisado': True, 'Novo aluno': True})

    def test_rascunho_persiste_sem_criar_aluno(self):
        guardar_rascunho(self.ata, self.rascunho)
        self.assertEqual(obter_rascunho(self.ata), self.rascunho)
        self.assertEqual(banco.listar_alunos(), [])

    def test_importacao_multiplos_homonimos_nao_conferida(self):
        ids = importar_revisados(self.ata, self.linhas, True)
        self.assertEqual(len(set(ids)), 2)
        self.assertEqual(banco.obter_situacao(ids[1], self.ata)['situacao'], 'TRANSFERIDA')
        self.assertTrue(all(not r['conferido'] for r in banco.listar_resultados(ids[0], self.ata)))
        self.assertTrue(all(r['nota'] is None for r in banco.listar_resultados(ids[1], self.ata)))

    def test_reenvio_nao_duplica(self):
        importar_revisados(self.ata, self.linhas, True)
        with self.assertRaises(ValueError):
            importar_revisados(self.ata, self.linhas, True)
        self.assertEqual(len(banco.listar_alunos()), 2)

    def test_rollback_segundo_id_inexistente(self):
        self.linhas[1].update({'Novo aluno': False, 'Aluno ID': 999})
        with self.assertRaises(ValueError):
            importar_revisados(self.ata, self.linhas, True)
        self.assertEqual(banco.listar_alunos(), [])
        with banco.conexao() as conn:
            self.assertEqual(conn.execute('SELECT COUNT(*) FROM resultados').fetchone()[0], 0)

    def test_id_existente_explicito_e_zero(self):
        aid = banco.salvar_aluno('Estudante Fictício')
        linha = self.linhas[0]
        linha.update({'Novo aluno': False, 'Aluno ID': aid, 'Matemática': 0})
        self.assertEqual(importar_revisados(self.ata, [linha], True), [aid])
        notas = {r['disciplina']: r['nota'] for r in banco.listar_resultados(aid, self.ata)}
        self.assertEqual(notas['Matemática'], '0')
        self.assertEqual(len(banco.listar_alunos()), 1)

    def test_bloqueios_revisao_identificacao_e_notas(self):
        for mudanca in ({'Revisado': False}, {'Novo aluno': False}, {'Aluno ID': 5}, {'Não mapeado': 'disciplina desconhecida'}, {'Matemática': 'ilegível'}, {'Linha': 0}):
            linhas = deepcopy(self.linhas)
            linhas[0].update(mudanca)
            with self.assertRaises(ValueError):
                importar_revisados(self.ata, linhas, True)
        with self.assertRaises(ValueError):
            importar_revisados(self.ata, self.linhas, False)
        self.assertEqual(banco.listar_alunos(), [])

    def test_cabecalho_alterado_invalida_conferencia(self):
        aid = importar_revisados(self.ata, [self.linhas[0]], True)[0]
        banco.confirmar_resultados(aid, self.ata)
        corrigir_cabecalho(self.ata, 2025, 9)
        self.assertFalse(any(r['conferido'] for r in banco.listar_resultados(aid, self.ata)))

    def test_nao_sobrescreve_resultado_existente(self):
        aid = banco.salvar_aluno('Estudante Fictício')
        banco.salvar_resultados(aid, self.ata, {'Matemática': '4'}, 'REPROVADO', '')
        self.linhas[0].update({'Novo aluno': False, 'Aluno ID': aid})
        with self.assertRaises(ValueError):
            importar_revisados(self.ata, [self.linhas[0]], True)
        self.assertEqual(banco.listar_resultados(aid, self.ata)[0]['nota'], '4')
