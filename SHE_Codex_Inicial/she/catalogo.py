"""Disciplinas e endereços preliminares — confirmar o mapeamento no documento."""
DISCIPLINAS = (
    "Língua Portuguesa",
    "Língua Inglesa",
    "Matemática",
    "Arte",
    "Ciências",
    "História",
    "Geografia",
    "Educação Física",
    "Ensino Religioso",
)

ALIASES = {
    "portugues": "Língua Portuguesa", "português": "Língua Portuguesa",
    "lingua portuguesa": "Língua Portuguesa", "língua portuguesa": "Língua Portuguesa",
    "ingles": "Língua Inglesa", "inglês": "Língua Inglesa",
    "lingua inglesa": "Língua Inglesa", "língua inglesa": "Língua Inglesa",
    "matematica": "Matemática", "matemática": "Matemática",
    "artes": "Arte", "arte": "Arte", "educacao artistica": "Arte",
    "ciências": "Ciências", "ciencias": "Ciências",
    "historia": "História", "história": "História",
    "geografia": "Geografia",
    "educacao fisica": "Educação Física", "educação física": "Educação Física",
    "ensino religioso": "Ensino Religioso",
}

# Notas no modelo Excel: colunas C/N para os anos finais.
COLUNAS_POR_ANO = {6: "T", 7: "V", 8: "X", 9: "Z"}
COLUNAS_CARGA_HORARIA = {6: "U", 7: "W", 8: "Y", 9: "AA"}
LINHAS_MODELO = {
    "Língua Portuguesa": 29,
    "Língua Inglesa": 30,
    "Geografia": 35,
    "História": 36,
    "Ciências": 40,
    "Matemática": 43,
    "Arte": 44,
    "Educação Física": 46,
    "Ensino Religioso": 48,
}
