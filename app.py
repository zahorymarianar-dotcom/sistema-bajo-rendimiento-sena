import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
DB_NAME = 'encuesta_sena.db'

def init_db():
    """Crea la base de datos y carga los 66 registros iniciales si no existe."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS respuestas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT,
            promedio REAL,
            horas TEXT,
            causal TEXT
        )
    ''')
    
    # Si la base de datos está vacía, insertamos los 66 registros base
    cursor.execute('SELECT COUNT(*) FROM respuestas')
    count = cursor.fetchone()[0]
    if count == 0:
        datos_base = []
        for _ in range(28):
            datos_base.append(('Estudiante Anónimo', 3.8, '1 - 3 Horas', 'Falta de hábitos y organización del tiempo'))
        for _ in range(22):
            datos_base.append(('Estudiante Anónimo', 3.2, '0 - 1 Hora', 'Falta de hábitos y organización del tiempo'))
        for _ in range(10):
            datos_base.append(('Estudiante Anónimo', 3.0, '3 - 5 Horas', 'Dificultad de comprensión de temas'))
        for _ in range(6):
            datos_base.append(('Estudiante Anónimo', 4.2, 'Más de 5 Horas', 'Problemas personales o emocionales'))
        
        cursor.executemany('''
            INSERT INTO respuestas (nombre, promedio, horas, causal)
            VALUES (?, ?, ?, ?)
        ''', datos_base)
        conn.commit()
    
    conn.close()

# Inicializar BD al arrancar
init_db()

@app.route('/')
def index():
    """Página principal con el formulario."""
    return render_template('index.html')

@app.route('/guardar', methods=['POST'])
def guardar():
    """Recibe la encuesta (ej. Fabio), la guarda en SQLite sumando el registro y redirige a gráficos."""
    nombre = request.form.get('nombre', 'Anónimo')
    promedio = float(request.form.get('promedio', 3.5))
    horas = request.form.get('horas', '1 - 3 Horas')
    causal = request.form.get('causal', 'Falta de hábitos y organización del tiempo')
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO respuestas (nombre, promedio, horas, causal)
        VALUES (?, ?, ?, ?)
    ''', (nombre, promedio, horas, causal))
    conn.commit()
    conn.close()
    
    return redirect(url_for('graficos'))

@app.route('/graficos')
def graficos():
    """Calcula los totales (las 67+ encuestas) y genera los gráficos dinámicos."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM respuestas')
    total_encuestas = cursor.fetchone()[0]
    
    cursor.execute('SELECT horas, COUNT(*) FROM respuestas GROUP BY horas')
    conteo_horas = dict(cursor.fetchall())
    
    cursor.execute('SELECT causal, COUNT(*) FROM respuestas GROUP BY causal')
    conteo_causales = dict(cursor.fetchall())
    
    conn.close()
    
    h_labels = ['0 - 1 Hora', '1 - 3 Horas', '3 - 5 Horas', 'Más de 5 Horas']
    h_data = [conteo_horas.get(label, 0) for label in h_labels]
    
    c_labels = list(conteo_causales.
