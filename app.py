from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3

app = Flask(__name__)
app.secret_key = 'sena_gaes5_secret'

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS estudiantes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            documento TEXT NOT NULL,
            ficha TEXT NOT NULL,
            motivo TEXT NOT NULL,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form['nombre']
        documento = request.form['documento']
        ficha = request.form['ficha']
        motivo = request.form['motivo']

        conn = get_db_connection()
        conn.execute('INSERT INTO estudiantes (nombre, documento, ficha, motivo) VALUES (?, ?, ?, ?)',
                     (nombre, documento, ficha, motivo))
        conn.commit()
        conn.close()
        
        flash('¡Registro enviado con éxito!')
        return redirect(url_for('index'))
    return render_template('registro.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/admin')
def admin():
    conn = get_db_connection()
    estudiantes = conn.execute('SELECT * FROM estudiantes ORDER BY fecha DESC').fetchall()
    
    # Contar diagnósticos para la gráfica de barras
    conteo = conn.execute('''
        SELECT motivo, COUNT(*) as cantidad 
        FROM estudiantes 
        GROUP BY motivo
    ''').fetchall()
    
    conn.close()
    
    labels = [row['motivo'] for row in conteo]
    valores = [row['cantidad'] for row in conteo]
    total = len(estudiantes)
    
    return render_template('admin.html', estudiantes=estudiantes, total=total, labels=labels, valores=valores)

if __name__ == '__main__':
    app.run(debug=True)
