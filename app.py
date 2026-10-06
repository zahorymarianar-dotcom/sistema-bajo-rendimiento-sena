from flask import Flask, render_template_string, request, redirect, url_for, flash
import sqlite3

app = Flask(__name__)
app.secret_key = 'sena_gaes5_secret_key'

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
            horas_estudio TEXT NOT NULL,
            materias_reprobadas INTEGER NOT NULL,
            factor_principal TEXT NOT NULL,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Si la base de datos está vacía, preinsertar muestra representativa según Bitácora 10 (N=15)
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM estudiantes')
    if cursor.fetchone()[0] == 0:
        datos_muestra = [
            ('Carlos Andrés Mendoza', '1012384920', '3157141', '0-1 horas', 3, 'Incidencia Docente'),
            ('Mariana Gómez Ruiz', '1092837411', '3157141', '1-2 horas', 2, 'Afectación Emocional'),
            ('Juan David Torres', '1029384756', '3157141', '0-1 horas', 4, 'Incidencia Docente'),
            ('Laura Valentina Silva', '1038475629', '3157141', '2-3 horas', 1, 'Falta de Hábitos'),
            ('Santiago Espitia', '1047562938', '3157141', '1-2 horas', 3, 'Incidencia Docente'),
            ('Paula Andrea Castro', '1056293847', '3157141', '3-4 horas', 0, 'Dificultad Técnica'),
            ('Kevin Alexis Ramírez', '1062938475', '3157141', '0-1 horas', 2, 'Afectación Emocional'),
            ('Daniela Morales', '1075629384', '3157141', '1-2 horas', 2, 'Incidencia Docente'),
            ('Andrés Felipe Vargas', '1084756293', '3157141', '4-5 horas', 0, 'Falta de Hábitos'),
            ('Valentina Ríos', '1093847562', '3157141', '0-1 horas', 3, 'Afectación Emocional'),
            ('Brayan Stiven Cruz', '1019283746', '3157141', '1-2 horas', 2, 'Incidencia Docente'),
            ('Sofía Hernández', '1028374651', '3157141', '2-3 horas', 1, 'Incidencia Docente'),
            ('Mateo Jaramillo', '1037465192', '3157141', '0-1 horas', 3, 'Afectación Emocional'),
            ('Isabella Gutiérrez', '1046519283', '3157141', 'Más de 5 horas', 0, 'Falta de Hábitos'),
            ('Camilo Esteban Peña', '1055192837', '3157141', '1-2 horas', 2, 'Incidencia Docente')
        ]
        cursor.executemany('''
            INSERT INTO estudiantes (nombre, documento, ficha, horas_estudio, materias_reprobadas, factor_principal)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', datos_muestra)
        
    conn.commit()
    conn.close()

init_db()

# --- PLANTILLAS HTML INTEGRADAS ---

NAVBAR = '''
<nav class="navbar navbar-expand-lg navbar-dark bg-primary shadow-sm">
  <div class="container">
    <a class="navbar-brand fw-bold" href="/">
      <i class="bi bi-journal-bookmark-fill me-2"></i>SENA GAES 5 | Ficha 3157141
    </a>
    <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
      <span class="navbar-toggler-icon"></span>
    </button>
    <div class="collapse navbar-collapse" id="navbarNav">
      <ul class="navbar-nav ms-auto">
        <li class="nav-item"><a class="nav-link" href="/"><i class="bi bi-house-door me-1"></i>Inicio</a></li>
        <li class="nav-item"><a class="nav-link" href="/registro"><i class="bi bi-clipboard-check me-1"></i>Encuesta</a></li>
        <li class="nav-item"><a class="nav-link btn btn-outline-light ms-lg-2 px-3 text-white" href="/login"><i class="bi bi-person-badge me-1"></i>Docentes</a></li>
      </ul>
    </div>
  </div>
</nav>
'''

BASE_LAYOUT = '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sistema de Control de Bajo Rendimiento - SENA</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body { background-color: #f8fafc; font-family: 'Segoe UI', system-ui, sans-serif; color: #1e293b; }
        .bg-primary { background-color: #1e3a8a !important; }
        .btn-primary { background-color: #2563eb; border-color: #2563eb; }
        .btn-primary:hover { background-color: #1d4ed8; }
        .card { border-radius: 12px; border: 1px solid #e2e8f0; }
        .metric-card { border-top: 4px solid #2563eb; }
    </style>
</head>
<body class="d-flex flex-column min-vh-100">
    ''' + NAVBAR + '''
    <main class="container py-4 flex-grow-1">
        {% with messages = get_flashed_messages() %}
          {% if messages %}
            {% for message in messages %}
              <div class="alert alert-success alert-dismissible fade show shadow-sm" role="alert">
                <i class="bi bi-check-circle-fill me-2"></i>{{ message }}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
              </div>
            {% endfor %}
          {% endif %}
        {% endwith %}
        {% block content %}{% endblock %}
    </main>
    <footer class="bg-dark text-white text-center py-3 mt-auto">
        <small>Técnico en Programación de Software | SENA Ficha 3157141 - GAES 5 &copy; 2026</small>
    </footer>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
'''

TEMPLATE_INDEX = BASE_LAYOUT.replace('{% block content %}{% endblock %}', '''
<div class="row align-items-center py-5">
    <div class="col-md-7">
        <span class="badge bg-primary mb-2 px-3 py-2 fs-6">Proyecto Formativo GAES 5</span>
        <h1 class="display-5 fw-bold text-dark">Sistema de Identificación y Control del Bajo Rendimiento Académico</h1>
        <p class="lead text-muted mt-3">Herramienta analítica para el diagnóstico, seguimiento y prevención de la deserción escolar en el programa Técnico en Programación de Software (Ficha 3157141).</p>
        <div class="d-flex gap-3 mt-4">
            <a href="/registro" class="btn btn-primary btn-lg px-4 shadow"><i class="bi bi-pencil-square me-2"></i>Diligenciar Encuesta</a>
            <a href="/login" class="btn btn-outline-secondary btn-lg px-4"><i class="bi bi-graph-up-arrow me-2"></i>Panel Docente</a>
        </div>
    </div>
    <div class="col-md-5 text-center mt-4 mt-md-0">
        <div class="card p-4 shadow-sm bg-white">
            <i class="bi bi-bar-chart-line-fill text-primary display-1 mb-3"></i>
            <h5 class="fw-bold">Monitoreo en Tiempo Real</h5>
            <p class="text-muted small">Consolidación automática de encuestas, generación de factores críticos e indicadores visuales para comités pedagógicos.</p>
        </div>
    </div>
</div>
''')

TEMPLATE_REGISTRO = BASE_LAYOUT.replace('{% block content %}{% endblock %}', '''
<div class="row justify-content-center">
    <div class="col-md-8">
        <div class="card shadow-sm">
            <div class="card-header bg-primary text-white p-3">
                <h4 class="mb-0 fs-5"><i class="bi bi-file-earmark-text me-2"></i>Instrumento de Diagnóstico Académico (Bitácora 10)</h4>
            </div>
            <div class="card-body p-4">
                <form action="/registro" method="POST">
                    <h6 class="fw-bold text-primary mb-3"><i class="bi bi-person-fill me-1"></i>1. Datos Básicos del Aprendiz</h6>
                    <div class="row g-3 mb-4">
                        <div class="col-md-6">
                            <label class="form-label fw-semibold">Nombre Completo</label>
                            <input type="text" name="nombre" class="form-control" placeholder="Ej: Maria Paula Perez" required>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label fw-semibold">Documento de Identidad</label>
                            <input type="text" name="documento" class="form-control" placeholder="Ej: 1012345678" required>
                        </div>
                        <div class="col-md-12">
                            <label class="form-label fw-semibold">Número de Ficha SENA</label>
                            <input type="text" name="ficha" class="form-control" value="3157141" required readonly>
                        </div>
                    </div>

                    <h6 class="fw-bold text-primary mb-3"><i class="bi bi-clock-history me-1"></i>2. Hábitos de Estudio y Rendimiento</h6>
                    <div class="row g-3 mb-4">
                        <div class="col-md-6">
                            <label class="form-label fw-semibold">Horas de Estudio Semanal en Casa</label>
                            <select name="horas_estudio" class="form-select" required>
                                <option value="" selected disabled>Seleccione una opción...</option>
                                <option value="0-1 horas">0 a 1 hora semanal</option>
                                <option value="1-2 horas">1 a 2 horas semanales</option>
                                <option value="2-3 horas">2 a 3 horas semanales</option>
                                <option value="3-4 horas">3 a 4 horas semanales</option>
                                <option value="4-5 horas">4 a 5 horas semanales</option>
                                <option value="Más de 5 horas">Más de 5 horas semanales</option>
                            </select>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label fw-semibold">Asignaturas / Materias Reprobadas</label>
                            <input type="number" min="0" max="10" name="materias_reprobadas" class="form-control" placeholder="Ej: 2" required>
                        </div>
                    </div>

                    <h6 class="fw-bold text-primary mb-3"><i class="bi bi-exclamation-triangle-fill me-1"></i>3. Causal Primaria del Resultado</h6>
                    <div class="mb-4">
                        <label class="form-label fw-semibold">¿Cuál considera que es el factor principal que incide en su desempeño?</label>
                        <select name="factor_principal" class="form-select" required>
                            <option value="" selected disabled>Seleccione el factor principal...</option>
                            <option value="Incidencia Docente">Metodología Docente / Estrategia Pedagógica</option>
                            <option value="Afectación Emocional">Factor Emocional / Dificultades Personales</option>
                            <option value="Falta de Hábitos">Organización de Tiempo / Hábitos de Estudio</option>
                            <option value="Dificultad Técnica">Complejidad Técnica del Software / Contenido</option>
                        </select>
                    </div>

                    <div class="d-grid gap-2">
                        <button type="submit" class="btn btn-primary btn-lg shadow-sm"><i class="bi bi-send-fill me-2"></i>Registrar Respuestas</button>
                    </div>
                </form>
            </div>
        </div>
    </div>
</div>
''')

TEMPLATE_LOGIN = BASE_LAYOUT.replace('{% block content %}{% endblock %}', '''
<div class="row justify-content-center py-5">
    <div class="col-md-5">
        <div class="card shadow">
            <div class="card-header bg-primary text-white text-center py-3">
                <h4 class="mb-0 fs-5"><i class="bi bi-shield-lock-fill me-2"></i>Acceso Docente / Instructor</h4>
            </div>
            <div class="card-body p-4">
                <form action="/login" method="POST">
                    <div class="mb-3">
                        <label class="form-label fw-semibold">Usuario SENA</label>
                        <input type="text" name="username" class="form-control" value="admin" required>
                    </div>
                    <div class="mb-4">
                        <label class="form-label fw-semibold">Contraseña</label>
                        <input type="password" name="password" class="form-control" value="1234" required>
                    </div>
                    <button type="submit" class="btn btn-primary w-100 btn-lg shadow-sm"><i class="bi bi-box-arrow-in-right me-2"></i>Ingresar al Dashboard</button>
                </form>
            </div>
        </div>
    </div>
</div>
''')

TEMPLATE_ADMIN = BASE_LAYOUT.replace('{% block content %}{% endblock %}', '''
<div class="d-flex justify-content-between align-items-center mb-4">
    <div>
        <h3 class="fw-bold mb-0 text-dark"><i class="bi bi-speedometer2 text-primary me-2"></i>Panel Analítico de Bajo Rendimiento</h3>
        <p class="text-muted mb-0">Consolidado estadístico del proyecto formativo - Ficha 3157141</p>
    </div>
    <a href="/registro" class="btn btn-outline-primary"><i class="bi bi-plus-circle me-1"></i>Nueva Encuesta</a>
</div>

<!-- TARJETAS METRICAS -->
<div class="row g-3 mb-4">
    <div class="col-md-3">
        <div class="card p-3 shadow-sm metric-card">
            <span class="text-muted small fw-bold text-uppercase">Total Encuestados</span>
            <h2 class="fw-bold text-primary my-1">{{ total }}</h2>
            <span class="text-secondary small">Muestra registrada (N)</span>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card p-3 shadow-sm metric-card" style="border-top-color: #dc2626;">
            <span class="text-muted small fw-bold text-uppercase">Prevalencia de Riesgo</span>
            <h2 class="fw-bold text-danger my-1">{{ prevalencia }}%</h2>
            <span class="text-secondary small">Estudiantes con 1+ materia reprobada</span>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card p-3 shadow-sm metric-card" style="border-top-color: #d97706;">
            <span class="text-muted small fw-bold text-uppercase">Prom. Materias Perdidas</span>
            <h2 class="fw-bold text-warning my-1">{{ prom_materias }}</h2>
            <span class="text-secondary small">Asignaturas por estudiante</span>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card p-3 shadow-sm metric-card" style="border-top-color: #0284c7;">
            <span class="text-muted small fw-bold text-uppercase">Incidencia Docente</span>
            <h2 class="fw-bold text-info my-1">{{ pct_docente }}%</h2>
            <span class="text-secondary small">Atribución a metodología</span>
        </div>
    </div>
</div>

<!-- GRAFICAS -->
<div class="row g-4 mb-4">
    <div class="col-md-6">
        <div class="card shadow-sm p-3 h-100">
            <h6 class="fw-bold text-dark mb-3"><i class="bi bi-bar-chart-fill me-2 text-primary"></i>1. Horas de Estudio Semanal en Casa</h6>
            <div style="position: relative; height:260px;">
                <canvas id="barHoras"></canvas>
            </div>
        </div>
    </div>
    <div class="col-md-6">
        <div class="card shadow-sm p-3 h-100">
            <h6 class="fw-bold text-dark mb-3"><i class="bi bi-pie-chart-fill me-2 text-primary"></i>2. Factores Determinantes del Bajo Rendimiento</h6>
            <div style="position: relative; height:260px;">
                <canvas id="pieFactores"></canvas>
            </div>
        </div>
    </div>
</div>

<!-- TABLA DE REGISTROS -->
<div class="card shadow-sm">
    <div class="card-header bg-white py-3">
        <h5 class="fw-bold mb-0 text-dark"><i class="bi bi-table me-2 text-primary"></i>Detalle de Encuestas Registradas</h5>
    </div>
    <div class="table-responsive">
        <table class="table table-hover align-middle mb-0">
            <thead class="table-light">
                <tr>
                    <th>Aprendiz</th>
                    <th>Documento</th>
                    <th>Ficha</th>
                    <th>Horas Estudio</th>
                    <th>Materias Reprobadas</th>
                    <th>Factor Principal</th>
                    <th>Estado de Riesgo</th>
                </tr>
            </thead>
            <tbody>
                {% for est in estudiantes %}
                <tr>
                    <td class="fw-semibold">{{ est['nombre'] }}</td>
                    <td>{{ est['documento'] }}</td>
                    <td><span class="badge bg-secondary">{{ est['ficha'] }}</span></td>
                    <td>{{ est['horas_estudio'] }}</td>
                    <td class="text-center fw-bold">{{ est['materias_reprobadas'] }}</td>
                    <td>{{ est['factor_principal'] }}</td>
                    <td>
                        {% if est['materias_reprobadas'] >= 2 %}
                            <span class="badge bg-danger"><i class="bi bi-exclamation-octagon-fill me-1"></i>Riesgo Alto</span>
                        {% elif est['materias_reprobadas'] == 1 %}
                            <span class="badge bg-warning text-dark"><i class="bi bi-exclamation-triangle-fill me-1"></i>Riesgo Moderado</span>
                        {% else %}
                            <span class="badge bg-success"><i class="bi bi-check-circle-fill me-1"></i>Sin Riesgo</span>
                        {% endif %}
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>

<script>
    // 1. GRAFICO DE BARRAS - HORAS DE ESTUDIO
    const ctxBar = document.getElementById('barHoras').getContext('2d');
    new Chart(ctxBar, {
        type: 'bar',
        data: {
            labels: {{ labels_horas | tojson }},
            datasets: [{
                label: 'Número de Estudiantes',
                data: {{ valores_horas | tojson }},
                backgroundColor: '#2563eb',
                borderRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: { y: { beginAtZero: true, ticks: { stepSize: 1 } } }
        }
    });

    // 2. GRAFICO DE TORTA / DONUT - FACTORES DETERMINANTES
    const ctxPie = document.getElementById('pieFactores').getContext('2d');
    new Chart(ctxPie, {
        type: 'doughnut',
        data: {
            labels: {{ labels_factores | tojson }},
            datasets: [{
                data: {{ valores_factores | tojson }},
                backgroundColor: ['#dc2626', '#d97706', '#2563eb', '#0284c7']
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { position: 'bottom' } }
        }
    });
</script>
''')

# --- RUTAS DE LA APLICACION ---

@app.route('/')
def index():
    return render_template_string(TEMPLATE_INDEX)

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form['nombre']
        documento = request.form['documento']
        ficha = request.form['ficha']
        horas_estudio = request.form['horas_estudio']
        materias_reprobadas = int(request.form['materias_reprobadas'])
        factor_principal = request.form['factor_principal']

        conn = get_db_connection()
        conn.execute('''
            INSERT INTO estudiantes (nombre, documento, ficha, horas_estudio, materias_reprobadas, factor_principal)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (nombre, documento, ficha, horas_estudio, materias_reprobadas, factor_principal))
        conn.commit()
        conn.close()
        
        flash('¡Encuesta y diagnóstico guardados exitosamente!')
        return redirect(url_for('index'))
    return render_template_string(TEMPLATE_REGISTRO)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        return redirect(url_for('admin'))
    return render_template_string(TEMPLATE_LOGIN)

@app.route('/admin')
def admin():
    conn = get_db_connection()
    estudiantes = conn.execute('SELECT * FROM estudiantes ORDER BY fecha DESC').fetchall()
    
    total = len(estudiantes)
    
    # Metricas clave
    con_reprobacion = sum(1 for e in estudiantes if e['materias_reprobadas'] > 0)
    prevalencia = round((con_reprobacion / total * 100), 1) if total > 0 else 0
    
    total_materias = sum(e['materias_reprobadas'] for e in estudiantes)
    prom_materias = round(total_materias / total, 2) if total > 0 else 0
    
    docente_cnt = sum(1 for e in estudiantes if e['factor_principal'] == 'Incidencia Docente')
    pct_docente = round((docente_cnt / total * 100), 1) if total > 0 else 0

    # 1. Datos para Gráfico de Horas de Estudio (Barras)
    rangos = ['0-1 horas', '1-2 horas', '2-3 horas', '3-4 horas', '4-5 horas', 'Más de 5 horas']
    valores_horas = []
    for r in rangos:
        cnt = sum(1 for e in estudiantes if e['horas_estudio'] == r)
        valores_horas.append(cnt)

    # 2. Datos para Gráfico de Factores (Torta/Donut)
    conteo_factores = conn.execute('''
        SELECT factor_principal, COUNT(*) as cantidad 
        FROM estudiantes 
        GROUP BY factor_principal
    ''').fetchall()
    
    conn.close()
    
    labels_factores = [row['factor_principal'] for row in conteo_factores]
    valores_factores = [row['cantidad'] for row in conteo_factores]
    
    return render_template_string(
        TEMPLATE_ADMIN,
        estudiantes=estudiantes,
        total=total,
        prevalencia=prevalencia,
        prom_materias=prom_materias,
        pct_docente=pct_docente,
        labels_horas=rangos,
        valores_horas=valores_horas,
        labels_factores=labels_factores,
        valores_factores=valores_factores
    )

if __name__ == '__main__':
    app.run(debug=True)
