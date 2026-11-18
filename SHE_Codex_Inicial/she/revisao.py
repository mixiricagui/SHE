"""Pendências de transcrição; não substituem os critérios oficiais de emissão."""
from .catalogo import DISCIPLINAS
from .validacao import normalizar_nota, SITUACOES


def pendencias_conferencia(resultados, situacao):
    pendencias = []
    por_disciplina = {r['disciplina']: r for r in resultados}
    for disciplina in DISCIPLINAS:
        registro = por_disciplina.get(disciplina)
        if registro is None or registro['nota'] is None:
            pendencias.append(f'{disciplina}: nota ausente; requer esclarecimento.')
            continue
        try:
            if normalizar_nota(registro['nota']) is None:
                pendencias.append(f'{disciplina}: nota ausente.')
        except ValueError:
            pendencias.append(f'{disciplina}: nota inválida ou ilegível.')
    if not situacao or situacao['situacao'] not in SITUACOES or situacao['situacao'] == 'PENDENTE':
        pendencias.append('Situação final pendente ou inválida.')
    elif situacao['situacao'] in ('TRANSFERIDO', 'TRANSFERIDA', 'OUTRO'):
        pendencias.append('Situação especial: tratamento institucional ainda não configurado.')
    return pendencias
