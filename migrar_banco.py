import shutil
import sqlite3

conn = sqlite3.connect("filmes.db")

# se a tabela nova ja existe, a migracao ja foi feita
ja_existe = conn.execute(
    "SELECT name FROM sqlite_master WHERE type='table' AND name='titulos'"
).fetchone()
if ja_existe:
    print("a migracao ja foi feita, nada a fazer")
    conn.close()
    raise SystemExit

conn.close()
shutil.copy("filmes.db", "filmes_backup.db")  # copia de seguranca
print("backup salvo em filmes_backup.db")

conn = sqlite3.connect("filmes.db")
conn.executescript("""
    CREATE TABLE titulos (
        id INTEGER,
        tipo TEXT,
        titulo TEXT,
        ano TEXT,
        sinopse TEXT,
        generos TEXT,
        palavras_chave TEXT,
        nota REAL,
        poster TEXT,
        PRIMARY KEY (id, tipo)
    );
    INSERT INTO titulos
        SELECT id, 'filme', titulo, ano, sinopse, generos, palavras_chave, nota, poster
        FROM filmes;

    CREATE TABLE embeddings_novo (
        id INTEGER,
        tipo TEXT,
        vetor BLOB,
        PRIMARY KEY (id, tipo)
    );
    INSERT INTO embeddings_novo SELECT filme_id, 'filme', vetor FROM embeddings;

    ALTER TABLE filmes RENAME TO filmes_antiga;
    ALTER TABLE embeddings RENAME TO embeddings_antiga;
    ALTER TABLE embeddings_novo RENAME TO embeddings;
""")
conn.commit()

print("titulos:", conn.execute("SELECT COUNT(*) FROM titulos").fetchone()[0])
print("embeddings:", conn.execute("SELECT COUNT(*) FROM embeddings").fetchone()[0])
conn.close()
