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
            estado_rendimiento TEXT DEFAULT 'Bajo Rendimiento',
            motivo TEXT NOT NULL,
            horas_estudio TEXT DEFAULT '1-3 horas',
            materias_reprobadas INTEGER DEFAULT 1,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Asegurar migración de columna si la BD ya existe
    try:
        conn.execute("ALTER TABLE estudiantes ADD COLUMN estado_rendimiento TEXT DEFAULT 'Bajo Rendimiento'")
    except sqlite3.OperationalError:
        pass

    try:
        conn.execute("ALTER TABLE estudiantes ADD COLUMN horas_estudio TEXT DEFAULT '1-3 horas'")
    except sqlite3.OperationalError:
        pass
        
    try:
        conn.execute("ALTER TABLE estudiantes ADD COLUMN materias_reprobadas INTEGER DEFAULT 1")
    except sqlite3.OperationalError:
        pass

    # Datos iniciales para demostración con varias fichas y estados
    cursor = conn.execute("SELECT COUNT(*) FROM estudiantes")
    if cursor.fetchone()[0] == 0:
        datos_semilla = [
            ('Carlos Eduardo Ruiz', '1012345678', '3157141', 'Bajo Rendimiento', 'Falta de Hábitos de Estudio', '0-1 horas', 3),
            ('Laura Daniela Gómez', '1023456789', '3157141', 'Buen Rendimiento', 'Ninguno / Excelente Desempeño', '+5 horas', 0),
            ('Andrés Felipe López', '1034567890', '3157141', 'Bajo Rendimiento', 'Afectación Emocional / Personal', '3-5 horas', 1),
            ('Sofia Valentina Torres', '1045678901', '2891234', 'Buen Rendimiento', 'Ninguno / Excelente Desempeño', '+5 horas', 0),
            ('Mateo Alejandro Ramírez', '1056789012', '2891234', 'Bajo Rendimiento', 'Falta de Hábitos de Estudio', '0-1 horas', 4),
            ('Camila Andrea Camacho', '1098722621', '3157141', 'Buen Rendimiento', 'Ninguno / Excelente Desempeño', '3-5 horas', 0)
        ]
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
    <title>SENA & Colcato - Diagnóstico de Rendimiento Académico</title>
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
                    <h1 class="display-5 fw-black text-dark mb-3">Diagnóstico y Comparativo de Rendimiento Académico</h1>
                    <h4 class="text-success fw-bold mb-4">Colegio Integrado Camilo Torres</h4>
                    <p class="lead text-secondary mb-4 mx-auto style='max-width: 750px;'">
                        Plataforma interactiva para evaluar el desempeño académico por fichas de formación, generando comparativos entre estudiantes de <strong>Buen Rendimiento</strong> y <strong>Bajo Rendimiento</strong>.
                    </p>
                    <div class="row g-4 my-4">
                        <div class="col-md-4">
                            <div class="card card-creative p-4 h-100">
                                <i class="bi bi-journal-text text-success fs-1 mb-2"></i>
                                <h5 class="fw-bold">Encuesta de Diagnóstico</h5>
                                <p class="text-muted small mb-0">Captura de estado académico, hábitos y causales por aprendiz.</p>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="card card-creative p-4 h-100">
                                <i class="bi bi-bar-chart-steps text-warning fs-1 mb-2"></i>
                                <h5 class="fw-bold">Gráficas por Ficha</h5>
                                <p class="text-muted small mb-0">Comparativa directa de aprendices con buen vs. bajo rendimiento por ficha.</p>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="card card-creative p-4 h-100">
                                <i class="bi bi-shield-exclamation text-danger fs-1 mb-2"></i>
                                <h5 class="fw-bold">Alertas Tempranas</h5>
                                <p class="text-muted small mb-0">Identificación inmediata de fichas con alto índice de vulnerabilidad.</p>
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
        estado_rendimiento = request.form.get('estado_rendimiento', 'Bajo Rendimiento')
        motivo = request.form.get('motivo', 'Falta de Hábitos de Estudio')
        horas = request.form.get('horas', '1-3 horas')
        materias = int(request.form.get('materias', 0))

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
                                <label class="form-label fw-bold"><i class="bi bi-bar-chart-line me-1 text-primary"></i> Estado de Rendimiento Académico</label>
                                <select name="estado_rendimiento" class="form-select form-select-lg rounded-3" required>
                                    <option value="Buen Rendimiento">Buen Rendimiento (Aprobando todas las materias)</option>
                                    <option value="Bajo Rendimiento" selected>Bajo Rendimiento (Con materias/resultados en riesgo)</option>
                                </select>
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
                            <div class="col-md-6">
                                <label class="form-label fw-bold"><i class="bi bi-x-circle me-1 text-danger"></i> Asignaturas Reprobadas</label>
                                <input type="number" name="materias" class="form-control form-control-lg rounded-3" min="0" max="15" value="1" required>
                            </div>
                            <div class="col-12">
                                <label class="form-label fw-bold"><i class="bi bi-exclamation-triangle me-1 text-warning"></i> Causa Determinante u Observación</label>
                                <select name="motivo" class="form-select form-select-lg rounded-3" required>
                                    <option value="Ninguno / Excelente Desempeño">Ninguno / Buen Desempeño Académico</option>
                                    <option value="Falta de Hábitos de Estudio">Falta de Hábitos de Estudio / Organización</option>
                                    <option value="Incidencia Docente / Metodología">Incidencia Docente / Metodología de Enseñanza</option>
                                    <option value="Afectación Emocional / Personal">Afectación Emocional / Situación Personal</option>
                                    <option value="Dificultad Técnica / Herramientas">Dificultad Técnica / Herramientas Digitales</option>
                                </select>
                            </div>
                        </div>
                        <div class="mt-4 pt-3 border-top">
                            <button type="submit" class="btn btn-creative w-100 py-3 fs-5">
                                <i class="bi bi-send-check me-2"></i> Registrar Diagnóstico
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
    
    # Consulta por Ficha y Estado de Rendimiento (Buen vs Bajo)
    fichas_query = conn.execute('''
        SELECT ficha, 
               SUM(CASE WHEN estado_rendimiento = 'Buen Rendimiento' THEN 1 ELSE 0 END) as buen_rendimiento,
               SUM(CASE WHEN estado_rendimiento = 'Bajo Rendimiento' THEN 1 ELSE 0 END) as bajo_rendimiento
        FROM estudiantes 
        GROUP BY ficha
    ''').fetchall()

    conteo_motivos = conn.execute('''
        SELECT motivo, COUNT(*) as cantidad 
        FROM estudiantes 
        GROUP BY motivo
    ''').fetchall()
    
    conn.close()

    labels_fichas = [row['ficha'] for row in fichas_query]
    datos_buen_rendimiento = [row['buen_rendimiento'] for row in fichas_query]
    datos_bajo_rendimiento = [row['bajo_rendimiento'] for row in fichas_query]

    labels_motivos = [row['motivo'] for row in conteo_motivos]
    valores_motivos = [row['cantidad'] for row in conteo_motivos]

    total_estudiantes = len(estudiantes)
    total_buen = sum(datos_buen_rendimiento)
    total_bajo = sum(datos_bajo_rendimiento)

    filas_tabla = ""
    for e in estudiantes:
        estado = e['estado_rendimiento'] if 'estado_rendimiento' in e.keys() and e['estado_rendimiento'] else 'Bajo Rendimiento'
        badge_estado = "bg-success" if estado == "Buen Rendimiento" else "bg-danger"
        m_count = e['materias_reprobadas'] if 'materias_reprobadas' in e.keys() and e['materias_reprobadas'] is not None else 0
        
        filas_tabla += f"""
        <tr>
            <td class="fw-bold">{e['nombre']}</td>
            <td>{e['documento']}</td>
            <td><span class="badge bg-secondary">{e['ficha']}</span></td>
            <td><span class="badge {badge_estado} fs-6 px-3">{estado}</span></td>
            <td><span class="badge bg-light text-dark border">{e['motivo']}</span></td>
            <td><i class="bi bi-clock me-1"></i> {e['horas_estudio']}</td>
            <td class="fw-bold text-center">{m_count}</td>
        </tr>
        """

    html_content = f'''
        <div class="animate__animated animate__fadeIn">
            <div class="d-flex justify-content-between align-items-center mb-4">
                <div>
                    <h2 class="fw-bold mb-1"><i class="bi bi-speedometer2 text-success me-2"></i> Dashboard Comparativo por Fichas</h2>
                    <p class="text-muted mb-0">Colegio Integrado Camilo Torres - San Vicente de Chucurí (SENA GAES 5)</p>
                </div>
                <button onclick="window.print()" class="btn btn-outline-dark fw-bold rounded-pill">
                    <i class="bi bi-printer me-1"></i> Imprimir Informe
                </button>
            </div>

            <!-- KPIs -->
            <div class="row g-4 mb-4">
                <div class="col-md-4">
                    <div class="card card-creative p-4 kpi-card border-primary">
                        <div class="d-flex justify-content-between align-items-center">
                            <div>
                                <small class="text-muted fw-bold">TOTAL APRENDICES</small>
                                <h2 class="display-5 fw-bold text-dark my-1">{total_estudiantes}</h2>
                                <small class="text-primary fw-bold"><i class="bi bi-people-fill me-1"></i> Registrados</small>
                            </div>
                            <i class="bi bi-people-fill fs-1 text-primary opacity-50"></i>
                        </div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card card-creative p-4 kpi-card border-success">
                        <div class="d-flex justify-content-between align-items-center">
                            <div>
                                <small class="text-muted fw-bold">BUEN RENDIMIENTO</small>
                                <h2 class="display-5 fw-bold text-success my-1">{total_buen}</h2>
                                <small class="text-success fw-bold"><i class="bi bi-check-circle-fill me-1"></i> Sin Riesgo</small>
                            </div>
                            <i class="bi bi-hand-thumbs-up-fill fs-1 text-success opacity-50"></i>
                        </div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card card-creative p-4 kpi-card border-danger">
                        <div class="d-flex justify-content-between align-items-center">
                            <div>
                                <small class="text-muted fw-bold">BAJO RENDIMIENTO</small>
                                <h2 class="display-5 fw-bold text-danger my-1">{total_bajo}</h2>
                                <small class="text-danger fw-bold"><i class="bi bi-exclamation-triangle-fill me-1"></i> En Riesgo</small>
                            </div>
                            <i class="bi bi-shield-x fs-1 text-danger opacity-50"></i>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Gráficos -->
            <div class="row g-4 mb-4">
                <div class="col-lg-7">
                    <div class="card card-creative p-4 h-100">
                        <h5 class="fw-bold mb-3"><i class="bi bi-bar-chart-grouped text-primary me-2"></i> Rendimiento de Aprendices por Ficha (Buen vs Bajo)</h5>
                        <div style="position: relative; height:320px;">
                            <canvas id="fichasChart"></canvas>
                        </div>
                    </div>
                </div>
                <div class="col-lg-5">
                    <div class="card card-creative p-4 h-100">
                        <h5 class="fw-bold mb-3"><i class="bi bi-pie-chart-fill text-success me-2"></i> Causas de Bajo Rendimiento</h5>
                        <div style="position: relative; height:320px;">
                            <canvas id="pieChart"></canvas>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Tabla -->
            <div class="card card-creative p-4">
                <div class="d-flex justify-content-between align-items-center mb-3">
                    <h5 class="fw-bold mb-0"><i class="bi bi-table me-2 text-dark"></i> Consolidado por Aprendiz y Ficha</h5>
                    <span class="badge bg-success">Colegio Camilo Torres</span>
                </div>
                <div class="table-responsive">
                    <table class="table table-hover align-middle table-custom">
                        <thead class="table-dark">
                            <tr>
                                <th>Nombre Aprendiz</th>
                                <th>Documento</th>
                                <th>Ficha</th>
                                <th>Estado Academic</th>
                                <th>Causa / Observación</th>
                                <th>Horas Estudio</th>
                                <th>Reprobadas</th>
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
            const labelsFichas = {labels_fichas};
            const datosBuen = {datos_buen_rendimiento};
            const datosBajo = {datos_bajo_rendimiento};

            const labelsMotivos = {labels_motivos};
            const valoresMotivos = {valores_motivos};

            // Gráfico de Barras Agrupadas por Ficha (Buen vs Bajo)
            new Chart(document.getElementById('fichasChart'), {{
                type: 'bar',
                data: {{
                    labels: labelsFichas,
                    datasets: [
                        {{
                            label: 'Buen Rendimiento',
                            data: datosBuen,
                            backgroundColor: '#39a900',
                            borderRadius: 6
                        }},
                        {{
                            label: 'Bajo Rendimiento',
                            data: datosBajo,
                            backgroundColor: '#dc3545',
                            borderRadius: 6
                        }}
                    ]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {{
                        y: {{ beginAtZero: true, ticks: {{ stepSize: 1 }} }}
                    }},
                    plugins: {{
                        legend: {{ position: 'top' }}
                    }}
                }}
            }});

            // Gráfico Torta
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
        </script>
    '''
    
    return render_template_string(HTML_LAYOUT.replace('{% block content %}{% endblock %}', html_content))

if __name__ == '__main__':
    app.run(debug=True)
