"""Persistência SQLite local, com IDs de aluno e registro de auditoria simplificado."""
import sqlite3
import hashlib
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from .config import BANCO, preparar_pastas
from .catalogo import ALIASES
from .validacao import normalizar_nota, padronizar_texto, validacao_serie, SITUACOES
from .revisao import pendencias_conferencia


@contextmanager
def conexao():
    preparar_pastas()
    conn = sqlite3.connect(BANCO)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        with conn:
            yield conn
    finally:
        conn.close()


def inicializar() -> None:
    with conexao() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS alunos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                matricula TEXT UNIQUE,
                data_nascimento TEXT,
                criado_em TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS atas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                arquivo TEXT NOT NULL,
                ano_letivo INTEGER NOT NULL,
                ano_escolar INTEGER NOT NULL,
                turma TEXT,
                turno TEXT,
                criado_em TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS resultados (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                aluno_id INTEGER NOT NULL REFERENCES alunos(id),
                ata_id INTEGER NOT NULL REFERENCES atas(id),
                disciplina TEXT NOT NULL,
                nota TEXT,
                conferido INTEGER NOT NULL DEFAULT 0,
                conferido_em TEXT,
                UNIQUE(aluno_id, ata_id, disciplina)
            );
            CREATE TABLE IF NOT EXISTS situacoes (
                aluno_id INTEGER NOT NULL REFERENCES alunos(id),
                ata_id INTEGER NOT NULL REFERENCES atas(id),
                situacao TEXT NOT NULL DEFAULT 'PENDENTE',
                observacao TEXT NOT NULL DEFAULT '',
                PRIMARY KEY(aluno_id, ata_id)
            );
            CREATE TABLE IF NOT EXISTS auditoria (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                instante TEXT NOT NULL,
                acao TEXT NOT NULL,
                detalhe TEXT NOT NULL
            );
        """)
        colunas = {r['name'] for r in conn.execute('PRAGMA table_info(atas)')}
        if 'sha256' not in colunas:
            conn.execute('ALTER TABLE atas ADD COLUMN sha256 TEXT')
        conn.execute('CREATE UNIQUE INDEX IF NOT EXISTS atas_hash ON atas(sha256)')


def momento() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def registrar_auditoria(conn: sqlite3.Connection, acao: str, detalhe: str) -> None:
    conn.execute("INSERT INTO auditoria(instante,acao,detalhe) VALUES(?,?,?)", (momento(), acao, detalhe))


def salvar_aluno(nome: str, matricula: str = "", nascimento: str = "") -> int:
    if len(nome.strip()) < 3:
        raise ValueError('Informe o nome completo.')
    if nascimento.strip():
        from datetime import date
        try:
            data = date.fromisoformat(nascimento.strip())
        except ValueError as exc:
            raise ValueError('Nascimento inválido; use AAAA-MM-DD.') from exc
        if data > date.today():
            raise ValueError('Nascimento não pode ser futuro.')
    with conexao() as conn:
        cur = conn.execute(
            "INSERT INTO alunos(nome,matricula,data_nascimento,criado_em) VALUES(?,?,?,?)",
            (nome.strip(), matricula.strip() or None, nascimento.strip() or None, momento()),
        )
        registrar_auditoria(conn, "ALUNO_CRIADO", f"id={cur.lastrowid}")
        return int(cur.lastrowid)


def listar_alunos():
    with conexao() as conn:
        return conn.execute("SELECT id,nome,matricula FROM alunos ORDER BY nome,id").fetchall()


def salvar_ata(caminho: Path, ano_letivo: int, ano_escolar: int, turma: str, turno: str) -> int:
    validacao_serie(ano_escolar)
    if not 1950 <= ano_letivo <= 2100:
        raise ValueError('Ano letivo inválido.')
    digest = hashlib.sha256(caminho.read_bytes()).hexdigest()
    with conexao() as conn:
        if conn.execute('SELECT id FROM atas WHERE sha256=?', (digest,)).fetchone():
            raise ValueError('Esta fotografia já foi importada. Utilize a ata existente.')
        cur = conn.execute(
            "INSERT INTO atas(arquivo,ano_letivo,ano_escolar,turma,turno,criado_em,sha256) VALUES(?,?,?,?,?,?,?)",
            (str(caminho), ano_letivo, ano_escolar, turma.strip(), turno.strip(), momento(), digest),
        )
        registrar_auditoria(conn, "ATA_IMPORTADA", f"id={cur.lastrowid}")
        return int(cur.lastrowid)


def listar_atas():
    with conexao() as conn:
        return conn.execute("SELECT id,arquivo,ano_letivo,ano_escolar,turma,turno FROM atas ORDER BY id DESC").fetchall()


def salvar_resultados(aluno_id: int, ata_id: int, entradas: dict[str, str | None], situacao: str, observacao: str) -> None:
    if situacao not in SITUACOES:
        raise ValueError('Situação inválida.')
    normalizadas = {}
    for rotulo, nota in entradas.items():
        disciplina = ALIASES.get(padronizar_texto(rotulo))
        if disciplina is None or disciplina in normalizadas:
            raise ValueError('Disciplina desconhecida ou repetida.')
        normalizadas[disciplina] = normalizar_nota('' if nota is None else nota)
    with conexao() as conn:
        conn.execute('UPDATE resultados SET conferido=0, conferido_em=NULL WHERE aluno_id=? AND ata_id=?', (aluno_id, ata_id))
        conn.execute("""INSERT INTO situacoes(aluno_id,ata_id,situacao,observacao) VALUES(?,?,?,?)
            ON CONFLICT(aluno_id,ata_id) DO UPDATE SET situacao=excluded.situacao,observacao=excluded.observacao""",
            (aluno_id, ata_id, situacao, observacao),
        )
        for disciplina, nota in normalizadas.items():
            conn.execute("""INSERT INTO resultados(aluno_id,ata_id,disciplina,nota,conferido,conferido_em)
                VALUES(?,?,?,?,0,NULL)
                ON CONFLICT(aluno_id,ata_id,disciplina)
                DO UPDATE SET nota=excluded.nota,conferido=0,conferido_em=NULL""",
                (aluno_id, ata_id, disciplina, nota),
            )
        registrar_auditoria(conn, "RESULTADOS_LANCADOS", f"aluno_id={aluno_id},ata_id={ata_id}")


def listar_resultados(aluno_id: int, ata_id: int):
    with conexao() as conn:
        return conn.execute("""SELECT disciplina,nota,conferido,conferido_em
            FROM resultados WHERE aluno_id=? AND ata_id=? ORDER BY disciplina""", (aluno_id, ata_id)).fetchall()


def obter_situacao(aluno_id: int, ata_id: int):
    with conexao() as conn:
        return conn.execute("SELECT situacao,observacao FROM situacoes WHERE aluno_id=? AND ata_id=?", (aluno_id, ata_id)).fetchone()


def confirmar_resultados(aluno_id: int, ata_id: int) -> None:
    """Confirmação registrada por ação explícita do operador na tela de conferência."""
    with conexao() as conn:
        resultados = conn.execute('SELECT disciplina,nota FROM resultados WHERE aluno_id=? AND ata_id=?', (aluno_id, ata_id)).fetchall()
        situacao = conn.execute('SELECT situacao FROM situacoes WHERE aluno_id=? AND ata_id=?', (aluno_id, ata_id)).fetchone()
        pendencias = pendencias_conferencia(resultados, situacao)
        if pendencias:
            raise ValueError('Conferência bloqueada: ' + ' '.join(pendencias))
        conn.execute("""UPDATE resultados SET conferido=1,conferido_em=?
            WHERE aluno_id=? AND ata_id=?""", (momento(), aluno_id, ata_id))
        registrar_auditoria(conn, "RESULTADOS_CONFERIDOS", f"aluno_id={aluno_id},ata_id={ata_id}")
