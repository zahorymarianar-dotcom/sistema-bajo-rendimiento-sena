from flask import Flask, request, redirect, url_for, render_template_string
import sqlite3

app = Flask(__name__)
app.secret_key = 'sena_colcato_gaes5_secret'

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
            horas_estudio TEXT DEFAULT '1-3 horas',
            materias_reprobadas INTEGER DEFAULT 1,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    try:
        conn.execute("ALTER TABLE estudiantes ADD COLUMN horas_estudio TEXT DEFAULT '1-3 horas'")
    except sqlite3.OperationalError:
        pass
        
    try:
        conn.execute("ALTER TABLE estudiantes ADD COLUMN materias_reprobadas INTEGER DEFAULT 1")
    except sqlite3.OperationalError:
        pass

    cursor = conn.execute("SELECT COUNT(*) FROM estudiantes")
    if cursor.fetchone()[0] == 0:
        datos_semilla = [
            ('Carlos Eduardo Ruiz', '1012345678', '3157141', 'Falta de Hábitos de Estudio', '0-1 horas', 3),
            ('Laura Daniela Gómez', '1023456789', '3157141', 'Incidencia Docente / Metodología', '1-3 horas', 2),
            ('Andrés Felipe López', '1034567890', '3157141', 'Afectación Emocional / Personal', '3-5 horas', 1),
            ('Sofia Valentina Torres', '1045678901', '3157141', 'Dificultad Técnica / Herramientas', '1-3 horas', 2),
            ('Mateo Alejandro Ramírez', '1056789012', '3157141', 'Falta de Hábitos de Estudio', '0-1 horas', 4)
        ]
        conn.executemany('''
            INSERT INTO estudiantes (nombre, documento, ficha, motivo, horas_estudio, materias_reprobadas)
            VALUES (?, ?, ?, ?, ?, ?)
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
    <title>SENA & Colcato - Diagnóstico de Bajo Rendimiento Académico</title>
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
                <span>Colegio Integrado Camilo Torres <span class="text-success">|</span> SENA GAES 5</span>
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
        <small>© 2026 Colegio Integrado Camilo Torres (San Vicente de Chucurí) & SENA GAES 5</small>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""

@app.route('/')
def index():
    html = HTML_LAYOUT.replace('{% block content %}{% endblock %}', '''
        <div class="row justify-content-center align-items-center min-vh-75 animate__animated animate__fadeIn">
            <div class="col-lg-10">
                <div class="hero-card p-5 text-center shadow-lg">
                    <span class="badge badge-sena mb-3"><i class="bi bi-geo-alt-fill me-1"></i> San Vicente de Chucurí</span>
                    <h1 class="display-5 fw-black text-dark mb-3">Diagnóstico de Bajo Rendimiento Académico</h1>
                    <h4 class="text-success fw-bold mb-4">Colegio Integrado Camilo Torres</h4>
                    <p class="lead text-secondary mb-4 mx-auto style='max-width: 750px;'">
                        Sistema inteligente diseñado para identificar, procesar y analizar las causas principales de bajo rendimiento académico en los estudiantes de la institución en articulación con el SENA.
                    </p>
                    <div class="row g-4 my-4">
                        <div class="col-md-4">
                            <div class="card card-creative p-4 h-100">
                                <i class="bi bi-journal-text text-success fs-1 mb-2"></i>
                                <h5 class="fw-bold">Encuesta Digital</h5>
                                <p class="text-muted small mb-0">Captura de datos de hábitos de estudio y factores académicos.</p>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="card card-creative p-4 h-100">
                                <i class="bi bi-pie-chart-fill text-warning fs-1 mb-2"></i>
                                <h5 class="fw-bold">Estadísticas Camilo Torres</h5>
                                <p class="text-muted small mb-0">Gráficos interactivos de causas de bajo rendimiento por ficha y curso.</p>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="card card-creative p-4 h-100">
                                <i class="bi bi-shield-exclamation text-danger fs-1 mb-2"></i>
                                <h5 class="fw-bold">Alertas Tempranas</h5>
                                <p class="text-muted small mb-0">Identificación de estudiantes con materias reprobadas para apoyo docente.</p>
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
    if request.method == 'POST':
        nombre = request.form.get('nombre', 'Anónimo')
        documento = request.form.get('documento', '0000')
        ficha = request.form.get('ficha', '3157141')
        motivo = request.form.get('motivo', 'Falta de Hábitos de Estudio')
        horas = request.form.get('horas', '1-3 horas')
        materias = int(request.form.get('materias', 1))

        conn = get_db_connection()
        conn.execute('''
            INSERT INTO estudiantes (nombre, documento, ficha, motivo, horas_estudio, materias_reprobadas) 
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (nombre, documento, ficha, motivo, horas, materias))
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
                            <h3 class="fw-bold mb-0">Encuesta de Diagnóstico Académico</h3>
                            <small class="text-muted">Colegio Integrado Camilo Torres - San Vicente de Chucurí</small>
                        </div>
                    </div>
                    <form method="POST">
                        <div class="row g-3">
                            <div class="col-md-6">
                                <label class="form-label fw-bold"><i class="bi bi-person me-1 text-success"></i> Nombre Completo del Estudiante</label>
                                <input type="text" name="nombre" class="form-control form-control-lg rounded-3" required placeholder="Ej: María Camila Pérez">
                            </div>
                            <div class="col-md-6">
                                <label class="form-label fw-bold"><i class="bi bi-card-heading me-1 text-success"></i> Documento de Identidad</label>
                                <input type="text" name="documento" class="form-control form-control-lg rounded-3" required placeholder="Ej: 1019823476">
                            </div>
                            <div class="col-md-6">
                                <label class="form-label fw-bold"><i class="bi bi-hash me-1 text-success"></i> Número de Ficha / Grupo</label>
                                <input type="text" name="ficha" class="form-control form-control-lg rounded-3" value="3157141" required placeholder="Ingrese la ficha">
                            </div>
                            <div class="col-md-6">
                                <label class="form-label fw-bold"><i class="bi bi-clock-history me-1 text-success"></i> Horas de Estudio Autónomo (Semanal)</label>
                                <select name="horas" class="form-select form-select-lg rounded-3" required>
                                    <option value="0-1 horas">0 a 1 horas (Baja dedicación)</option>
                                    <option value="1-3 horas" selected>1 a 3 horas (Dedicación media)</option>
                                    <option value="3-5 horas">3 a 5 horas (Buena dedicación)</option>
                                    <option value="+5 horas">Más de 5 horas (Excelente)</option>
                                </select>
                            </div>
                            <div class="col-12">
                                <label class="form-label fw-bold"><i class="bi bi-exclamation-triangle me-1 text-danger"></i> Causa Principal de Bajo Rendimiento</label>
                                <select name="motivo" class="form-select form-select-lg rounded-3" required>
                                    <option value="Falta de Hábitos de Estudio">Falta de Hábitos de Estudio / Organización</option>
                                    <option value="Incidencia Docente / Metodología">Incidencia Docente / Metodología de Enseñanza</option>
                                    <option value="Afectación Emocional / Personal">Afectación Emocional / Situación Personal</option>
                                    <option value="Dificultad Técnica / Herramientas">Dificultad Técnica / Herramientas Digitales</option>
                                </select>
                            </div>
                            <div class="col-12">
                                <label class="form-label fw-bold"><i class="bi bi-x-circle me-1 text-danger"></i> Cantidad de Asignaturas / Competencias Perdedoras</label>
                                <input type="number" name="materias" class="form-control form-control-lg rounded-3" min="0" max="15" value="1" required>
                            </div>
                        </div>
                        <div class="mt-4 pt-3 border-top">
                            <button type="submit" class="btn btn-creative w-100 py-3 fs-5">
                                <i class="bi bi-send-check me-2"></i> Enviar Diagnóstico
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    ''')
    return render_template_string(html)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        return redirect(url_for('admin'))

    html = HTML_LAYOUT.replace('{% block content %}{% endblock %}', '''
        <div class="row justify-content-center align-items-center min-vh-50 animate__animated animate__zoomIn">
            <div class="col-md-5">
                <div class="card card-creative p-5 text-center">
                    <div class="mb-4">
                        <i class="bi bi-shield-lock-fill text-success" style="font-size: 3.5rem;"></i>
                        <h3 class="fw-bold mt-2">Acceso Docente y Directivos</h3>
                        <p class="text-muted small">Colegio Integrado Camilo Torres</p>
                    </div>
                    <form method="POST">
                        <div class="form-floating mb-3">
                            <input type="text" name="user" class="form-control rounded-3" id="user" placeholder="Usuario" value="admin" required>
                            <label for="user">Usuario</label>
                        </div>
                        <div class="form-floating mb-4">
                            <input type="password" name="pass" class="form-control rounded-3" id="pass" placeholder="Contraseña" value="1234" required>
                            <label for="pass">Contraseña</label>
                        </div>
                        <button type="submit" class="btn btn-creative w-100 py-3">
                            <i class="bi bi-box-arrow-in-right me-2"></i> Ingresar al Dashboard
                        </button>
                    </form>
                </div>
            </div>
        </div>
    ''')
    return render_template_string(html)

@app.route('/admin')
def admin():
    conn = get_db_connection()
    estudiantes = conn.execute('SELECT * FROM estudiantes ORDER BY fecha DESC').fetchall()
    
    conteo_motivos = conn.execute('''
        SELECT motivo, COUNT(*) as cantidad 
        FROM estudiantes 
        GROUP BY motivo
    ''').fetchall()

    conteo_horas = conn.execute('''
        SELECT horas_estudio, COUNT(*) as cantidad 
        FROM estudiantes 
        GROUP BY horas_estudio
    ''').fetchall()
    
    conn.close()

    labels_motivos = [row['motivo'] for row in conteo_motivos]
    valores_motivos = [row['cantidad'] for row in conteo_motivos]

    labels_horas = [row['horas_estudio'] for row in conteo_horas]
    valores_horas = [row['cantidad'] for row in conteo_horas]

    total_estudiantes = len(estudiantes)
    total_materias = sum([e['materias_reprobadas'] if 'materias_reprobadas' in e.keys() and e['materias_reprobadas'] else 1 for e in estudiantes])
    promedio_materias = round(total_materias / total_estudiantes, 1) if total_estudiantes > 0 else 0

    filas_tabla = ""
    for e in estudiantes:
        m_count = e['materias_reprobadas'] if 'materias_reprobadas' in e.keys() and e['materias_reprobadas'] else 1
        badge_class = "bg-danger" if m_count >= 3 else ("bg-warning text-dark" if m_count == 2 else "bg-info text-dark")
        
        filas_tabla += f"""
        <tr>
            <td class="fw-bold">{e['nombre']}</td>
            <td>{e['documento']}</td>
            <td><span class="badge bg-secondary">{e['ficha']}</span></td>
            <td><span class="badge bg-light text-dark border">{e['motivo']}</span></td>
            <td><i class="bi bi-clock me-1"></i> {e['horas_estudio']}</td>
            <td><span class="badge {badge_class} rounded-pill fs-6 px-3">{m_count} Asignatura(s)</span></td>
        </tr>
        """

    html_content = f'''
        <div class="animate__animated animate__fadeIn">
            <div class="d-flex justify-content-between align-items-center mb-4">
                <div>
                    <h2 class="fw-bold mb-1"><i class="bi bi-speedometer2 text-success me-2"></i> Dashboard Estadístico</h2>
                    <p class="text-muted mb-0">Colegio Integrado Camilo Torres - San Vicente de Chucurí (SENA GAES 5)</p>
                </div>
                <button onclick="window.print()" class="btn btn-outline-dark fw-bold rounded-pill">
                    <i class="bi bi-printer me-1"></i> Imprimir Informe
                </button>
            </div>

            <!-- KPIs -->
            <div class="row g-4 mb-4">
                <div class="col-md-4">
                    <div class="card card-creative p-4 kpi-card border-success">
                        <div class="d-flex justify-content-between align-items-center">
                            <div>
                                <small class="text-muted fw-bold">ESTUDIANTES REGISTRADOS</small>
                                <h2 class="display-5 fw-bold text-dark my-1">{total_estudiantes}</h2>
                                <small class="text-success fw-bold"><i class="bi bi-check-circle-fill me-1"></i> Muestra Procesada</small>
                            </div>
                            <i class="bi bi-people-fill fs-1 text-success opacity-50"></i>
                        </div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card card-creative p-4 kpi-card border-warning">
                        <div class="d-flex justify-content-between align-items-center">
                            <div>
                                <small class="text-muted fw-bold">PROMEDIO PERDIDO</small>
                                <h2 class="display-5 fw-bold text-dark my-1">{promedio_materias}</h2>
                                <small class="text-warning fw-bold"><i class="bi bi-exclamation-triangle-fill me-1"></i> Asignaturas / Estudiante</small>
                            </div>
                            <i class="bi bi-journal-x fs-1 text-warning opacity-50"></i>
                        </div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card card-creative p-4 kpi-card border-danger">
                        <div class="d-flex justify-content-between align-items-center">
                            <div>
                                <small class="text-muted fw-bold">ALERTA ACADÉMICA</small>
                                <h2 class="display-5 fw-bold text-danger my-1">ACTIVA</h2>
                                <small class="text-danger fw-bold"><i class="bi bi-shield-x me-1"></i> Seguimiento Pedagógico</small>
                            </div>
                            <i class="bi bi-activity fs-1 text-danger opacity-50"></i>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Gráficos -->
            <div class="row g-4 mb-4">
                <div class="col-lg-6">
                    <div class="card card-creative p-4 h-100">
                        <h5 class="fw-bold mb-3"><i class="bi bi-pie-chart-fill text-success me-2"></i> Causas Principales de Bajo Rendimiento</h5>
                        <div style="position: relative; height:300px;">
                            <canvas id="pieChart"></canvas>
                        </div>
                    </div>
                </div>
                <div class="col-lg-6">
                    <div class="card card-creative p-4 h-100">
                        <h5 class="fw-bold mb-3"><i class="bi bi-bar-chart-line-fill text-primary me-2"></i> Dedicación en Horas de Estudio</h5>
                        <div style="position: relative; height:300px;">
                            <canvas id="barChart"></canvas>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Tabla -->
            <div class="card card-creative p-4">
                <div class="d-flex justify-content-between align-items-center mb-3">
                    <h5 class="fw-bold mb-0"><i class="bi bi-table me-2 text-dark"></i> Consolidado de Estudiantes Encuestados</h5>
                    <span class="badge bg-success">Colegio Camilo Torres</span>
                </div>
                <div class="table-responsive">
                    <table class="table table-hover align-middle table-custom">
                        <thead class="table-dark">
                            <tr>
                                <th>Nombre Estudiante</th>
                                <th>Documento</th>
                                <th>Ficha / Grupo</th>
                                <th>Causa Principal</th>
                                <th>Horas Estudio</th>
                                <th>Materias Reprobadas</th>
                            </tr>
                        </thead>
                        <tbody>
                            {filas_tabla}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <script>
            const labelsMotivos = {labels_motivos};
            const valoresMotivos = {valores_motivos};

            const labelsHoras = {labels_horas};
            const valoresHoras = {valores_horas};

            new Chart(document.getElementById('pieChart'), {{
                type: 'doughnut',
                data: {{
                    labels: labelsMotivos,
                    datasets: [{{
                        data: valoresMotivos,
                        backgroundColor: ['#39a900', '#ffc107', '#dc3545', '#0dcaf0', '#6c757d'],
                        borderWidth: 2
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{ legend: {{ position: 'bottom' }} }}
                }}
            }});

            new Chart(document.getElementById('barChart'), {{
                type: 'bar',
                data: {{
                    labels: labelsHoras,
                    datasets: [{{
                        label: 'Cantidad de Estudiantes',
                        data: valoresHoras,
                        backgroundColor: '#00324d',
                        borderRadius: 8
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{ legend: {{ display: false }} }}
                }}
            }});
        </script>
    '''
    
    return render_template_string(HTML_LAYOUT.replace('{% block content %}{% endblock %}', html_content))

if __name__ == '__main__':
    app.run(debug=True)
