"""Testes que rodam sem dados de estudantes."""
import unittest
from she.validacao import normalizar_nota, validacao_serie


class TestNotas(unittest.TestCase):
    def test_virgula_decimal(self):
        self.assertEqual(normalizar_nota("7,5"), "7.5")

    def test_zero_nao_e_ausente(self):
        self.assertEqual(normalizar_nota("0"), "0")
        self.assertIsNone(normalizar_nota(""))

    def test_nota_ilegivel_rejeitada(self):
        with self.assertRaises(ValueError):
            normalizar_nota("8B")

    def test_faixa(self):
        with self.assertRaises(ValueError):
            normalizar_nota("11")

    def test_serie(self):
        validacao_serie(8)
        with self.assertRaises(ValueError):
            validacao_serie(5)


if __name__ == "__main__":
    unittest.main()
