import sqlite3

def criar_banco():
    conn = sqlite3.connect('vendas_magistral.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lotes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            produtor TEXT,
            especie TEXT,
            categoria TEXT,
            quantidade INTEGER,
            chegada TEXT,
            liberacao TEXT,
            status TEXT DEFAULT 'Em Descanso'
        )
    ''')
    conn.commit()
    conn.close()

if __name__ == '__main__':
    criar_banco()