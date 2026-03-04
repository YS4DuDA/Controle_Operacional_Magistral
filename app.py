import os
import sqlite3
import pytz
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'magistral_tcc_senai_key'

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
    # Tabela de Produtores com CNPJ
    db.execute('''CREATE TABLE IF NOT EXISTS produtores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome_completo TEXT, nome_propriedade TEXT, localidade TEXT, cnpj TEXT)''')
    # Tabela de Lotes
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

@app.route('/registrar_produtor', methods=['GET', 'POST'])
def registrar_produtor():
    if request.method == 'POST':
        nome = request.form['nome'].strip()
        prop = request.form['propriedade'].strip()
        loc = request.form['localidade'].strip()
        cnpj = request.form['cnpj'].strip()

        if len(cnpj) != 14 or cnpj == cnpj[0] * 14:
            flash('ERRO: CNPJ INVÁLIDO. INSIRA EXATAMENTE 14 NÚMEROS.')
            return render_template('registrar_produtor.html')

        db = get_db()
        
        existente = db.execute('''SELECT * FROM produtores 
                                  WHERE cnpj = ? OR LOWER(nome_propriedade) = ?''', 
                               (cnpj, prop.lower())).fetchone()
        
        if existente:
            db.close()
            flash('ERRO: CNPJ OU NOME DA PROPRIEDADE JÁ CADASTRADOS NO SISTEMA.')
            return render_template('registrar_produtor.html')

        db.execute('INSERT INTO produtores (nome_completo, nome_propriedade, localidade, cnpj) VALUES (?,?,?,?)', 
                   (nome, prop, loc, cnpj))
        db.commit()
        db.close()
        return redirect(url_for('cadastro'))
    return render_template('registrar_produtor.html')

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    db = get_db()
    if request.method == 'POST':
        nome_digitado = request.form['nome_propriedade'].strip().lower()
        try:
            qtd = int(request.form['quantidade'])
            if qtd <= 0: raise ValueError
        except ValueError:
            flash('ERRO: QUANTIDADE INVÁLIDA.')
            return redirect(url_for('cadastro'))

        produtor = db.execute('SELECT id FROM produtores WHERE LOWER(nome_propriedade) = ?', (nome_digitado,)).fetchone()
        if not produtor:
            flash(f'PROPRIEDADE "{nome_digitado.upper()}" NÃO ENCONTRADA.')
            return redirect(url_for('cadastro'))

        file = request.files.get('nota_fiscal')
        filename = secure_filename(file.filename) if file and file.filename != '' else None
        if filename: file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        fuso_br = pytz.timezone('America/Sao_Paulo')
        hor_notif = datetime.now(fuso_br).strftime('%Y-%m-%d %H:%M:%S')

        especie = request.form.get('especie', 'Bovino')
        
        if especie == 'Suino':
            categoria = 'Suíno'
        elif especie == 'Ovino':
            categoria = 'Ovino'
        else:
            categoria = request.form.get('categoria')
            if not categoria:
                categoria = 'Boi' 
        db.execute('''INSERT INTO lotes (produtor_id, especie, categoria, quantidade, status, horario_notificacao, nota_fiscal) 
                      VALUES (?,?,?,?,?,?,?)''', (produtor['id'], especie, categoria, qtd, 'Em Trânsito', hor_notif, filename))
        db.commit()
        db.close()
        return redirect(url_for('sucesso'))
    
    produtores = db.execute('SELECT * FROM produtores').fetchall()
    db.close()
    return render_template('cadastro.html', produtores=produtores)

@app.route('/confirmar_chegada/<int:lote_id>')
def confirmar_chegada(lote_id):
    db = get_db()
    fuso_br = pytz.timezone('America/Sao_Paulo')
    agora = datetime.now(fuso_br)
    chegada_real = agora.strftime('%Y-%m-%d %H:%M:%S')
    liberacao = (agora + timedelta(hours=2)).strftime('%Y-%m-%d %H:%M:%S')
    db.execute('UPDATE lotes SET status = "Em Descanso", horario_chegada_real = ?, liberacao = ? WHERE id = ?', (chegada_real, liberacao, lote_id))
    db.commit()
    db.close()
    return redirect(url_for('dashboard'))

@app.route('/producao')
def monitor_producao():
    db = get_db()
    fuso_br = pytz.timezone('America/Sao_Paulo')
    agora = datetime.now(fuso_br).strftime('%Y-%m-%d %H:%M:%S')
    hoje = datetime.now(fuso_br).strftime('%Y-%m-%d')
    lotes_hoje = db.execute('''SELECT l.*, p.nome_propriedade FROM lotes l JOIN produtores p ON l.produtor_id = p.id 
                               WHERE l.horario_chegada_real LIKE ? ORDER BY l.liberacao ASC''', (hoje + '%',)).fetchall()
    total_gado = sum(lote['quantidade'] for lote in lotes_hoje)
    db.close()
    return render_template('producao.html', lotes=lotes_hoje, total=total_gado, data=hoje, agora=agora)

@app.route('/sucesso')
def sucesso():
    return render_template('sucesso.html')

if __name__ == '__main__':
    app.run(debug=True)