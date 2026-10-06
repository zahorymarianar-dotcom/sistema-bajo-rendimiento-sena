from flask import Flask, request, redirect, url_for, render_template_string
import sqlite3

app = Flask(__name__)
app.secret_key = 'sena_gaes5_secret'

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    # Crear tabla base si no existe
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
    
    # Agregar columnas si la tabla ya existía de versiones anteriores
    try:
        conn.execute("ALTER TABLE estudiantes ADD COLUMN horas_estudio TEXT DEFAULT '1-3 horas'")
    except sqlite3.OperationalError:
        pass
        
    try:
        conn.execute("ALTER TABLE estudiantes ADD COLUMN materias_reprobadas INTEGER DEFAULT 1")
    except sqlite3.OperationalError:
        pass

    # Insertar datos iniciales de prueba si está vacía para que las gráficas no salgan en blanco
    cursor = conn.execute("SELECT COUNT(*) FROM estudiantes")
    if cursor.fetchone()[0] == 0:
        datos_iniciales = [
            ('Carlos Ruiz', '1012345678', '3157141', 'Falta de Hábitos de Estudio', '0-1 horas', 3),
            ('Laura Gómez', '1023456789', '3157141', 'Incidencia Docente / Metodología', '1-3 horas', 2),
            ('Andrés López', '1034567890', '3157141', 'Afectación Emocional / Personal', '3-5 horas', 1),
            ('Sofia Torres', '1045678901', '3157141', 'Dificultad Técnica / Herramientas', '1-3 horas', 2),
            ('Mateo Ramírez', '1056789012', '3157141', 'Falta de Hábitos de Estudio', '0-1 horas', 4)
        ]
        conn.executemany('''
            INSERT INTO estudiantes (nombre, documento, ficha, motivo, horas_estudio, materias_reprobadas)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', datos_iniciales)

    conn.commit()
    conn.close()

init_db()

HTML_LAYOUT = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SENA - Diagnóstico de Bajo Rendimiento</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body { background-color: #f8f9fa; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        .navbar-sena { background-color: #39a900; }
        .card-custom { border-radius: 12px; border: none; box-shadow: 0 4px 12px rgba(0,0,0,0.08); }
        .btn-sena { background-color: #39a900; color: white; font-weight: bold; }
        .btn-sena:hover { background-color: #2e8600; color: white; }
    </style>
</head>
<body>
    <nav class="navbar navbar-dark navbar-sena mb-4">
        <div class="container">
            <a class="navbar-brand fw-bold" href="/">SENA | GAES 5 - Control de Bajo Rendimiento</a>
            <div>
                <a href="/" class="btn btn-sm btn-outline-light me-2">Inicio</a>
                <a href="/registro" class="btn btn-sm btn-outline-light me-2">Encuesta</a>
                <a href="/login" class="btn btn-sm btn-light text-success fw-bold">Acceso Docentes</a>
            </div>
        </div>
    </nav>
    <div class="container mb-5">
        {% block content %}{% endblock %}
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    html = HTML_LAYOUT.replace('{% block content %}{% endblock %}', '''
        <div class="row justify-content-center">
            <div class="col-md-8 text-center mt-4">
                <div class="card card-custom p-5">
                    <h1 class="display-5 text-success fw-bold">Sistema de Diagnóstico de Bajo Rendimiento</h1>
                    <p class="lead mt-3 text-secondary">Herramienta de recolección de datos y análisis estadístico para la Ficha 3157141 (SENA).</p>
                    <hr class="my-4">
                    <div class="d-grid gap-3 d-sm-flex justify-content-sm-center">
                        <a href="/registro" class="btn btn-sena btn-lg px-4">Responder Encuesta</a>
                        <a href="/login" class="btn btn-outline-secondary btn-lg px-4">Panel de Administración</a>
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
        <div class="row justify-content-center">
            <div class="col-md-6">
                <div class="card card-custom p-4">
                    <h3 class="fw-bold text-success text-center mb-3">Encuesta de Diagnóstico</h3>
                    <form method="POST">
                        <div class="mb-3">
                            <label class="form-label fw-bold">Nombre Completo</label>
                            <input type="text" name="nombre" class="form-control" required placeholder="Ej: Maria Perez">
                        </div>
                        <div class="mb-3">
                            <label class="form-label fw-bold">Documento de Identidad</label>
                            <input type="text" name="documento" class="form-control" required placeholder="Ej: 1012345678">
                        </div>
                        <div class="mb-3">
                            <label class="form-label fw-bold">Número de Ficha</label>
                            <input type="text" name="ficha" class="form-control" value="3157141" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label fw-bold">Factor Principal de Bajo Rendimiento</label>
                            <select name="motivo" class="form-select" required>
                                <option value="Falta de Hábitos de Estudio">Falta de Hábitos de Estudio</option>
                                <option value="Incidencia Docente / Metodología">Incidencia Docente / Metodología</option>
                                <option value="Afectación Emocional / Personal">Afectación Emocional / Personal</option>
                                <option value="Dificultad Técnica / Herramientas">Dificultad Técnica / Herramientas</option>
                            </select>
                        </div>
                        <div class="mb-3">
                            <label class="form-label fw-bold">Horas de Estudio Semanal fuera del SENA</label>
                            <select name="horas" class="form-select" required>
                                <option value="0-1 horas">0 a 1 horas</option>
                                <option value="1-3 horas">1 a 3 horas</option>
                                <option value="3-5 horas">3 a 5 horas</option>
                                <option value="+5 horas">Más de 5 horas</option>
                            </select>
                        </div>
                        <div class="mb-3">
                            <label class="form-label fw-bold">Materias / Competencias Reprobadas</label>
                            <input type="number" name="materias" class="form-control" min="0" max="10" value="1" required>
                        </div>
                        <button type="submit" class="btn btn-sena w-100 mt-2">Guardar Respuesta</button>
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
        <div class="row justify-content-center">
            <div class="col-md-4">
                <div class="card card-custom p-4">
                    <h4 class="fw-bold text-center text-success mb-3">Acceso Docentes</h4>
                    <form method="POST">
                        <div class="mb-3">
                            <label class="form-label fw-bold">Usuario</label>
                            <input type="text" name="user" class="form-control" required placeholder="admin">
                        </div>
                        <div class="mb-3">
                            <label class="form-label fw-bold">Contraseña</label>
                            <input type="password" name="pass" class="form-control" required placeholder="****">
                        </div>
                        <button type="submit" class="btn btn-sena w-100">Ingresar al Panel</button>
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
    
    conn.close()

    labels = [row['motivo'] for row in conteo_motivos]
    valores = [row['cantidad'] for row in conteo_motivos]

    filas_tabla = ""
    for e in estudiantes:
        filas_tabla += f"""
        <tr>
            <td>{e['nombre']}</td>
            <td>{e['documento']}</td>
            <td>{e['ficha']}</td>
            <td><span class="badge bg-warning text-dark">{e['motivo']}</span></td>
            <td>{e['horas_estudio'] if 'horas_estudio' in e.keys() and e['horas_estudio'] else '1-3 horas'}</td>
            <td>{e['materias_reprobadas'] if 'materias_reprobadas' in e.keys() and e['materias_reprobadas'] else 1}</td>
        </tr>
        """

    html_content = f'''
        <h2 class="fw-bold mb-4 text-dark">Panel de Administración e Indicadores</h2>
        <div class="row mb-4">
            <div class="col-md-4">
                <div class="card card-custom p-3 bg-white border-start border-success border-4">
                    <h6 class="text-muted">Total Respuestas Registradas</h6>
                    <h3 class="fw-bold text-success">{len(estudiantes)}</h3>
                </div>
            </div>
        </div>

        <div class="row mb-4">
            <div class="col-md-6 mb-3">
                <div class="card card-custom p-4">
                    <h5 class="fw-bold mb-3">Factores Determinantes (Gráfico de Torta)</h5>
                    <canvas id="pieChart"></canvas>
                </div>
            </div>
            <div class="col-md-6 mb-3">
                <div class="card card-custom p-4">
                    <h5 class="fw-bold mb-3">Distribución por Causa (Gráfico de Barras)</h5>
                    <canvas id="barChart"></canvas>
                </div>
            </div>
        </div>

        <div class="card card-custom p-4">
            <h5 class="fw-bold mb-3">Registro de Estudiantes Encuestados</h5>
            <div class="table-responsive">
                <table class="table table-hover align-middle">
                    <thead class="table-light">
                        <tr>
                            <th>Nombre</th>
                            <th>Documento</th>
                            <th>Ficha</th>
                            <th>Causa Principal</th>
                            <th>Horas Estudio</th>
                            <th>Materias Perdedoras</th>
                        </tr>
                    </thead>
                    <tbody>
                        {filas_tabla}
                    </tbody>
                </table>
            </div>
        </div>

        <script>
            const labels = {labels};
            const dataValues = {valores};

            new Chart(document.getElementById('pieChart'), {{
                type: 'pie',
                data: {{
                    labels: labels,
                    datasets: [{{
                        data: dataValues,
                        backgroundColor: ['#39a900', '#ffc107', '#dc3545', '#0dcaf0']
                    }}]
                }}
            }});

            new Chart(document.getElementById('barChart'), {{
                type: 'bar',
                data: {{
                    labels: labels,
                    datasets: [{{
                        label: 'Cantidad de Estudiantes',
                        data: dataValues,
                        backgroundColor: '#39a900'
                    }}]
                }}
            }});
        </script>
    '''
    
    return render_template_string(HTML_LAYOUT.replace('{% block content %}{% endblock %}', html_content))

if __name__ == '__main__':
    app.run(debug=True)
