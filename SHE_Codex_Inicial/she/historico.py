"""Consolidação por ID: preserva atas distintas e sinaliza conflitos por série."""
from .banco import conexao


def consultar_historico(aluno_id: int):
    with conexao() as conn:
        registros = conn.execute('''SELECT a.id AS ata_id,a.ano_letivo,a.ano_escolar,
            r.disciplina,r.nota,r.conferido,s.situacao
            FROM resultados r JOIN atas a ON a.id=r.ata_id
            LEFT JOIN situacoes s ON s.aluno_id=r.aluno_id AND s.ata_id=r.ata_id
            WHERE r.aluno_id=? ORDER BY a.ano_escolar,a.ano_letivo,a.id,r.disciplina''', (aluno_id,)).fetchall()
    por_serie = {}
    for r in registros:
        por_serie.setdefault(r['ano_escolar'], set()).add(r['ata_id'])
    conflitos = [serie for serie, atas in por_serie.items() if len(atas) > 1]
    return [dict(r) for r in registros], conflitos
