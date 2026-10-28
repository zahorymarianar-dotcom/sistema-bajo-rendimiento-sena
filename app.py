from flask import Flask, request, redirect, url_for, render_template_string
import sqlite3
import random

app = Flask(__name__)
app.secret_key = 'sena_colcato_gaes5_secret'

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    
    # Crear la tabla limpia si no existe
    conn.execute('''
        CREATE TABLE IF NOT EXISTS estudiantes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            documento TEXT NOT NULL,
            ficha TEXT NOT NULL,
            estado_rendimiento TEXT DEFAULT 'Bajo Rendimiento',
            motivo TEXT NOT NULL,
            horas_estudio TEXT DEFAULT '1-3 horas',
            materias_reprobadas INTEGER DEFAULT 1,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Asegurar columnas si la tabla ya existía previamente
    columnas = [col['name'] for col in conn.execute("PRAGMA table_info(estudiantes)").fetchall()]
    if 'estado_rendimiento' not in columnas:
        conn.execute("ALTER TABLE estudiantes ADD COLUMN estado_rendimiento TEXT DEFAULT 'Bajo Rendimiento'")
    if 'horas_estudio' not in columnas:
        conn.execute("ALTER TABLE estudiantes ADD COLUMN horas_estudio TEXT DEFAULT '1-3 horas'")
    if 'materias_reprobadas' not in columnas:
        conn.execute("ALTER TABLE estudiantes ADD COLUMN materias_reprobadas INTEGER DEFAULT 1")

    # Precargar exactamente las 66 encuestas con nombres variados si está vacía
    cursor = conn.execute("SELECT COUNT(*) FROM estudiantes")
    if cursor.fetchone()[0] == 0:
        nombres = [
            "Cielo Marcela", "Karoll Dayana", "Angie Paola", "Valeria Sofía", "Yuliana Andrea", 
            "Mariana Sofía", "Laura Valentina", "Sara Nicole", "Daniela Alejandra", "Paula Andrea",
            "Camila Andrea", "Natalia Sofía", "Gabriela Isabel", "Tatiana Milena", "Diana Marcela",
            "Karen Dayana", "Luisa Fernanda", "Valentina Rueda", "Manuela Gómez", "Alejandra Torres",
            "Paola Andrea", "Melany Johana", "Shaira Nicole", "Danna Sofía", "Giseth Tatiana",
            "Kelly Johana", "Brenda Juliana", "Nicole Vanessa", "Zahory Mariana", "Ximena Lucía"
        ]
        
        fichas = ["3157141", "2891234", "3157142", "2891235"]
        motivos = [
            "Falta de Hábitos de Estudio / Organización",
            "Dificultad Técnica / Herramientas",
            "Afectación Emocional / Situación Personal",
            "Incidencia Docente / Metodología"
        ]
        horas_opciones = ["0-1 horas", "1-3 horas", "3-5 horas", "+5 horas"]
        
        datos_semilla = []
        for _ in range(66):
            nombre_aleatorio = f"{random.choice(nombres)} {random.choice(['Pérez', 'Rodríguez', 'Gómez', 'López', 'Torres', 'Ramírez', 'Díaz', 'Castro', 'Silva', 'Rojas'])}"
            doc_aleatorio = str(random.randint(1000000000, 1099999999))
            ficha_aleatoria = random.choice(fichas)
            motivo_aleatorio = random.choice(motivos)
            horas_aleatorias = random.choice(horas_opciones)
            materias_aleatorias = random.randint(1, 4)
            
            datos_semilla.append((
                nombre_aleatorio, 
                doc_aleatorio, 
                ficha_aleatoria, 
                'Bajo Rendimiento', 
                motivo_aleatorio, 
                horas_aleatorias, 
                materias_aleatorias
            ))
        
        conn.executemany('''
            INSERT INTO estudiantes (nombre, documento, ficha, estado_rendimiento, motivo, horas_estudio, materias_reprobadas)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', datos_semilla)

    conn.commit()
    conn.close()

init_db()

HTML_LAYOUT = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Colegio Integrado Camilo Torres - Diagnóstico Académico</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/animate.css/4.1.1/animate.min.css"/>
    <style>
        :root {
            --sena-green: #39a900;
            --sena-dark: #00324d;
            --sena-accent: #00843d;
        }
        body {
            background: #f0f4f8;
            font-family: 'Plus Jakarta Sans', system-ui, -apple-system, sans-serif;
            color: #1e293b;
        }
        .navbar-custom {
            background: linear-gradient(135deg, var(--sena-dark) 0%, #001f31 100%);
            box-shadow: 0 4px 20px rgba(0,0,0,0.15);
        }
        .hero-card {
            background: linear-gradient(135deg, rgba(57, 169, 0, 0.08) 0%, rgba(0, 50, 77, 0.05) 100%);
            border: 1px solid rgba(57, 169, 0, 0.2);
            border-radius: 20px;
        }
        .card-creative {
            border: none;
            border-radius: 18px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.05);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            background: #ffffff;
        }
        .card-creative:hover {
            transform: translateY(-3px);
            box-shadow: 0 12px 32px rgba(0,0,0,0.08);
        }
        .badge-sena {
            background: var(--sena-green);
            color: white;
            font-weight: 600;
            padding: 6px 14px;
            border-radius: 50px;
        }
        .btn-creative {
            background: linear-gradient(135deg, var(--sena-green) 0%, var(--sena-accent) 100%);
            color: white;
            border: none;
            border-radius: 12px;
            padding: 12px 28px;
            font-weight: 700;
            box-shadow: 0 4px 15px rgba(57, 169, 0, 0.3);
            transition: all 0.3s ease;
        }
        .btn-creative:hover {
            color: white;
            transform: scale(1.02);
            box-shadow: 0 6px 20px rgba(57, 169, 0, 0.4);
        }
        .kpi-card {
