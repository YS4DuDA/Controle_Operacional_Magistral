import os
import sqlite3
import pytz
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'magistral_industrial_secret'

# CONFIGURAÇÕES DE DIRETÓRIO
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'magistral_abate.db')
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static/uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    if not os.path.exists(UPLOAD_FOLDER): os.makedirs(UPLOAD_FOLDER)
    db = get_db()
    db.execute('''CREATE TABLE IF NOT EXISTS produtores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome_completo TEXT, nome_propriedade TEXT, localidade TEXT)''')
    db.execute('''CREATE TABLE IF NOT EXISTS lotes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        produtor_id INTEGER, especie TEXT, categoria TEXT, quantidade INTEGER,
        status TEXT, horario_notificacao TEXT, horario_chegada_real TEXT,
        liberacao TEXT, nota_fiscal TEXT,
        FOREIGN KEY (produtor_id) REFERENCES produtores (id))''')
    db.commit()
    db.close()

init_db()

@app.route('/')
def dashboard():
    db = get_db()
    fuso_br = pytz.timezone('America/Sao_Paulo')
    agora = datetime.now(fuso_br).strftime('%Y-%m-%d %H:%M:%S')
    query = '''
        SELECT l.*, p.nome_propriedade 
        FROM lotes l JOIN produtores p ON l.produtor_id = p.id 
        WHERE l.status = 'Em Trânsito' OR (l.status = 'Em Descanso' AND l.liberacao > ?)
        ORDER BY l.status DESC, l.liberacao ASC
    '''
    lotes = db.execute(query, (agora,)).fetchall()
    db.close()
    return render_template('dashboard.html', lotes=lotes)

@app.route('/confirmar_chegada/<int:lote_id>')
def confirmar_chegada(lote_id):
    db = get_db()
    fuso_br = pytz.timezone('America/Sao_Paulo')
    agora = datetime.now(fuso_br)
    chegada_real = agora.strftime('%Y-%m-%d %H:%M:%S')
    liberacao = (agora + timedelta(hours=2)).strftime('%Y-%m-%d %H:%M:%S')
    db.execute('''UPDATE lotes SET status = 'Em Descanso', 
                  horario_chegada_real = ?, liberacao = ? 
                  WHERE id = ?''', (chegada_real, liberacao, lote_id))
    db.commit()
    db.close()
    return redirect(url_for('dashboard'))

@app.route('/registrar_produtor', methods=['GET', 'POST'])
def registrar_produtor():
    if request.method == 'POST':
        nome, prop, loc = request.form['nome'], request.form['propriedade'], request.form['localidade']
        db = get_db()
        db.execute('INSERT INTO produtores (nome_completo, nome_propriedade, localidade) VALUES (?,?,?)', (nome, prop, loc))
        db.commit()
        db.close()
        return redirect(url_for('cadastro'))
    return render_template('registrar_produtor.html')

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    db = get_db()
    if request.method == 'POST':
        nome_digitado = request.form['nome_propriedade']
        esp, cat, qtd = request.form['especie'], request.form['categoria'], request.form['quantidade']
        produtor = db.execute('SELECT id FROM produtores WHERE nome_propriedade = ?', (nome_digitado,)).fetchone()
        
        if not produtor:
            flash(f'PROPRIEDADE "{nome_digitado}" NÃO ENCONTRADA.')
            return redirect(url_for('cadastro'))

        p_id = produtor['id']
        file = request.files.get('nota_fiscal')
        filename = secure_filename(file.filename) if file and file.filename != '' else None
        if filename: file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        fuso_br = pytz.timezone('America/Sao_Paulo')
        horario_notificacao = datetime.now(fuso_br).strftime('%Y-%m-%d %H:%M:%S')

        db.execute('''INSERT INTO lotes (produtor_id, especie, categoria, quantidade, status, horario_notificacao, nota_fiscal) 
                      VALUES (?,?,?,?,?,?,?)''', (p_id, esp, cat, qtd, 'Em Trânsito', horario_notificacao, filename))
        db.commit()
        db.close()
        return redirect(url_for('sucesso'))
    
    produtores = db.execute('SELECT * FROM produtores').fetchall()
    db.close()
    return render_template('cadastro.html', produtores=produtores)

@app.route('/sucesso')
def sucesso():
    return render_template('sucesso.html')

if __name__ == '__main__':
    app.run(debug=True)