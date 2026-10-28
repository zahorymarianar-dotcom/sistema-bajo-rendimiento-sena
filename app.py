from flask import Flask, request, redirect, url_for, render_template_string
import sqlite3

app = Flask(__name__)
app.secret_key = 'sena_colcato_gaes5_secret'

def get_db_connection():
    conn = sqlite3.connect('database.db', timeout=10)
    conn.row_factory = sqlite3.Row
    return conn

def asegurar_db():
    conn = get_db_connection()
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
    
    columnas = [col['name'] for col in conn.execute("PRAGMA table_info(estudiantes)").fetchall()]
    if 'estado_rendimiento' not in columnas:
        conn.execute("ALTER TABLE estudiantes ADD COLUMN estado_rendimiento TEXT DEFAULT 'Bajo Rendimiento'")
    if 'horas_estudio' not in columnas:
        conn.execute("ALTER TABLE estudiantes ADD COLUMN horas_estudio TEXT DEFAULT '1-3 horas'")
    if 'materias_reprobadas' not in columnas:
        conn.execute("ALTER TABLE estudiantes ADD COLUMN materias_reprobadas INTEGER DEFAULT 1")

    cursor = conn.execute("SELECT COUNT(*) FROM estudiantes")
    if cursor.fetchone()[0] == 0:
        nombres_base = [
            ("Cielo Marcela Pérez", "3157141", "Falta de Hábitos de Estudio / Organización", "1-3 horas", 2),
            ("Karoll Dayana Rodríguez", "3157141", "Dificultad Técnica / Herramientas", "0-1 horas", 3),
            ("Angie Paola Gómez", "2891234", "Afectación Emocional / Situación Personal", "3-5 horas", 1),
            ("Valeria Sofía López", "3157141", "Incidencia Docente / Metodología", "+5 horas", 2),
            ("Yuliana Andrea Torres", "2891235", "Falta de Hábitos de Estudio / Organización", "1-3 horas", 2),
            ("Mariana Sofía Ramírez", "3157141", "Dificultad Técnica / Herramientas", "0-1 horas", 4),
            ("Laura Valentina Díaz", "3157142", "Afectación Emocional / Situación Personal", "3-5 horas", 1),
            ("Sara Nicole Castro", "3157141", "Incidencia Docente / Metodología", "+5 horas", 2)
        ]
        
        datos_semilla = []
        for i in range(66):
            info = nombres_base[i % len(nombres_base)]
            nombre = f"{info[0].split()[0]} {info[0].split()[1]} Estudiante {i+1}"
            doc = str(1010000000 + i)
            ficha = info[1]
            motivo = info[2]
            horas = info[3]
            materias = info[4]
            datos_semilla.append((nombre, doc, ficha, 'Bajo Rendimiento', motivo, horas, materias))
            
        conn.executemany('''
            INSERT INTO estudiantes (nombre, documento, ficha, estado_rendimiento, motivo, horas_estudio, materias_reprobadas)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', datos_semilla)
        conn.commit()
    
    conn.close()

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
            border-left: 5px solid var(--sena-green);
        }
        .table-custom {
            border-radius: 12px;
            overflow: hidden;
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark navbar-custom py-3 sticky-top">
        <div class="container">
            <a class="navbar-brand d-flex align-items-center gap-2 font-monospace fw-bold fs-5" href="/">
                <i class="bi bi-building-fill-gear text-warning fs-4"></i>
                <span>Colegio Integrado Camilo Torres <span class="text-success">|</span> Ficha 3157141</span>
            </a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto gap-2">
                    <li class="nav-item">
                        <a class="nav-link text-white fw-semibold px-3" href="/"><i class="bi bi-house-door me-1"></i> Inicio</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link text-white fw-semibold px-3" href="/registro"><i class="bi bi-clipboard2-check me-1"></i> Encuesta Estudiantil</a>
                    </li>
                    <li class="nav-item">
                        <a class="btn btn-warning text-dark fw-bold px-4 ms-lg-3 rounded-pill" href="/login">
                            <i class="bi bi-person-workspace me-1"></i> Panel Docente
                        </a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <div class="container my-5">
        {% block content %}{% endblock %}
    </div>

    <footer class="text-center py-4 text-muted border-top mt-5 bg-white">
        <small>© 2026 Colegio Integrado Camilo Torres (San Vicente de Chucurí)</small>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""

@app.route('/')
def index():
    asegurar_db()
    html = HTML_LAYOUT.replace('{% block content %}{% endblock %}', '''
        <div class="row justify-content-center align-items-center min-vh-75 animate__animated animate__fadeIn">
            <div class="col-lg-10">
                <div class="hero-card p-5 text-center shadow-lg">
                    <span class="badge badge-sena mb-3"><i class="bi bi-geo-alt-fill me-1"></i> San Vicente de Chucurí</span>
                    <h1 class="display-5 fw-black text-dark mb-3">Sistema de Diagnóstico del Bajo Rendimiento Académico</h1>
                    <h4 class="text-success fw-bold mb-4">Colegio Integrado Camilo Torres</h4>
                    <p class="lead text-secondary mb-4 mx-auto style='max-width: 750px;'">
                        Plataforma interactiva institucional para evaluar el desempeño académico, registrar encuestas y visualizar el consolidado en tiempo real.
                    </p>
                    <div class="row g-4 my-4">
                        <div class="col-md-4">
                            <div class="card card-creative p-4 h-100">
                                <i class="bi bi-journal-text text-success fs-1 mb-2"></i>
                                <h5 class="fw-bold">Encuesta de Diagnóstico</h5>
                                <p class="text-muted small mb-0">Captura de estado académico, hábitos y causales por estudiante.</p>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="card card-creative p-4 h-100">
                                <i class="bi bi-bar-chart-steps text-warning fs-1 mb-2"></i>
                                <h5 class="fw-bold">Gráficas Dinámicas</h5>
                                <p class="text-muted small mb-0">Visualización inmediata de las encuestas registradas.</p>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="card card-creative p-4 h-100">
                                <i class="bi bi-shield-exclamation text-danger fs-1 mb-2"></i>
                                <h5 class="fw-bold">Control y Estadísticas</h5>
                                <p class="text-muted small mb-0">Monitoreo de factores asociados al rendimiento académico.</p>
                            </div>
                        </div>
                    </div>
                    <div class="d-flex justify-content-center gap-3 mt-4">
                        <a href="/registro" class="btn btn-creative btn-lg"><i class="bi bi-pencil-square me-2"></i> Diligenciar Encuesta</a>
                        <a href="/login" class="btn btn-outline-dark btn-lg rounded-3 fw-bold px-4"><i class="bi bi-speedometer2 me-2"></i> Panel de Control</a>
                    </div>
                </div>
            </div>
        </div>
    ''')
    return render_template_string(html)

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    asegurar_db()
    if request.method == 'POST':
        nombre = request.form.get('nombre', 'Anónimo')
        documento = request.form.get('documento', '0000')
        ficha = request.form.get('ficha', '3157141')
        estado_rendimiento = request.form.get('estado_rendimiento', 'Bajo Rendimiento')
        motivo = request.form.get('motivo', 'Falta de Hábitos de Estudio / Organización')
        horas = request.form.get('horas', '1-3 horas')
        materias = int(request.form.get('materias', 1))

        conn = get_db_connection()
        conn.execute('''
            INSERT INTO estudiantes (nombre, documento, ficha, estado_rendimiento, motivo, horas_estudio, materias_reprobadas) 
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (nombre, documento, ficha, estado_rendimiento, motivo, horas, materias))
        conn.commit()
        conn.close()

        return redirect(url_for('admin'))

    html = HTML_LAYOUT.replace('{% block content %}{% endblock %}', '''
        <div class="row justify-content-center animate__animated animate__fadeInUp">
            <div class="col-lg-8">
                <div class="card card-creative p-5">
                    <div class="d-flex align-items-center gap-3 mb-4 border-bottom pb-3">
                        <div class="bg-success text-white rounded-circle p-3 d-flex align-items-center justify-content-center" style="width: 50px; height: 50px;">
                            <i class="bi bi-card-checklist fs-4"></i>
                        </div>
                        <div>
                            <h3 class="fw-bold mb-0">Encuesta de Rendimiento Académico</h3>
                            <small class="text-muted">Colegio Integrado Camilo Torres - San Vicente de Chucurí</small>
                        </div>
                    </div>
                    <form method="POST">
                        <div class="row g-3">
                            <div class="col-md-6">
                                <label class="form-label fw-bold"><i class="bi bi-person me-1 text-success"></i> Nombre Completo del Estudiante</label>
                                <input type="text" name="nombre" class="form-control form-control-lg rounded-3" required placeholder="">
                            </div>
                            <div class="col-md-6">
                                <label class="form-label fw-bold"><i class="bi bi-card-heading me-1 text-success"></i> Documento de Identidad</label>
                                <input type="text" name="documento" class="form-control form-control-lg rounded-3" required placeholder="">
                            </div>
                            <div class="col-md-6">
                                <label class="form-label fw-bold"><i class="bi bi-hash me-1 text-success"></i> Número de Ficha / Grupo</label>
                                <input type="text" name="ficha" class="form-control form-control-lg rounded-3" value="3157141" required placeholder="">
                            </div>
                            <div class="col-md-6">
                                <label class="form-label fw-bold"><i class="bi bi-bar-chart-line me-1 text-primary"></i> Estado de Rendimiento Académico</label>
                                <select name="estado_rendimiento" class="form-select form-select-lg rounded-3" required>
                                    <option value="Buen Rendimiento">Buen Rendimiento (Aprobando todas)</option>
                                    <option value="Bajo Rendimiento" selected>Bajo Rendimiento (En riesgo)</option>
                                </select>
                            </div>
                            <div class="col-md-6">
                                <label class="form-label fw-bold"><i class="bi bi-clock-history me-1 text-success"></i> Horas de Estudio Autónomo</label>
                                <select name="horas" class="form-select form
