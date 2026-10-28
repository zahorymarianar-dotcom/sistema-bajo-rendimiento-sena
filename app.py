
from flask import Flask, request, redirect, url_for, render_template_string
import sqlite3
import json
from html import escape

app = Flask(__name__)
app.secret_key = "sena_colcato_gaes5_secret"

DATABASE = "database.db"


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS estudiantes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            documento TEXT NOT NULL,
            ficha TEXT NOT NULL,
            estado_rendimiento TEXT DEFAULT 'Bajo Rendimiento',
            motivo TEXT NOT NULL,
            horas_estudio TEXT DEFAULT '1-3 horas',
            materias_reprobadas INTEGER DEFAULT 1,
            origen TEXT DEFAULT 'Simulado',
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    columnas = [
        ("estado_rendimiento", "TEXT DEFAULT 'Bajo Rendimiento'"),
        ("horas_estudio", "TEXT DEFAULT '1-3 horas'"),
        ("materias_reprobadas", "INTEGER DEFAULT 1"),
        ("origen", "TEXT DEFAULT 'Simulado'")
    ]

    for nombre_columna, tipo in columnas:
        try:
            conn.execute(
                f"ALTER TABLE estudiantes ADD COLUMN {nombre_columna} {tipo}"
            )
        except sqlite3.OperationalError:
            pass

    total = conn.execute(
        "SELECT COUNT(*) FROM estudiantes"
    ).fetchone()[0]

    faltan = max(0, 66 - total)

    nombres = [
        "Sara", "Valentina", "Sofia", "Camila", "Isabella",
        "Mariana", "Laura", "Daniela", "Gabriela", "Natalia",
        "Juliana", "Paula", "Andrea", "Manuela", "Luciana",
        "Alejandra", "Daniel", "Samuel", "Mateo", "Sebastian",
        "Nicolas", "Juan", "David"
    ]

    apellidos = [
        "Perez", "Acevedo", "Rodriguez", "Gomez", "Rojas",
        "Martinez", "Torres", "Ramirez", "Castro", "Mendoza",
        "Moreno", "Garcia", "Vargas", "Lopez", "Suarez"
    ]

    motivos = [
        "Falta de Hábitos de Estudio",
        "Ninguno / Excelente Desempeño",
        "Afectación Emocional / Personal",
        "Incidencia Docente / Metodología",
        "Dificultad Técnica / Herramientas"
    ]

    horas_opciones = [
        "0-1 horas", "1-3 horas", "3-5 horas", "+5 horas"
    ]

    datos = []

    for i in range(faltan):
        nombre = (
            f"{nombres[i % len(nombres)]} "
            f"{apellidos[(i // len(nombres)) % len(apellidos)]}"
        )

        buen_rendimiento = i % 3 != 1

        if buen_rendimiento:
            estado = "Buen Rendimiento"
            motivo = "Ninguno / Excelente Desempeño"
            materias = 0
        else:
            estado = "Bajo Rendimiento"
            motivo = motivos[i % len(motivos)]

            if motivo == "Ninguno / Excelente Desempeño":
                motivo = "Falta de Hábitos de Estudio"

            materias = (i % 4) + 1

        ficha = "3157141" if i % 2 == 0 else "2891234"
        horas = horas_opciones[i % len(horas_opciones)]

        datos.append((
            nombre,
            f"SIM-TI-{i + 1:04d}",
            ficha,
            estado,
            motivo,
            horas,
            materias,
            "Simulado"
        ))

    if datos:
        conn.executemany("""
            INSERT INTO estudiantes
            (nombre, documento, ficha, estado_rendimiento,
             motivo, horas_estudio, materias_reprobadas, origen)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, datos)

    conn.commit()
    conn.close()


init_db()


HTML_LAYOUT = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <title>Diagnóstico de Rendimiento Académico</title>

    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css"
          rel="stylesheet">

    <link rel="stylesheet"
          href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css">

    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

    <link rel="stylesheet"
          href="https://cdnjs.cloudflare.com/ajax/libs/animate.css/4.1.1/animate.min.css">

    <style>
        :root {
            --sena-green: #39a900;
            --sena-dark: #00324d;
            --sena-accent: #00843d;
        }

        body {
            background: #f0f4f8;
            font-family: system-ui, sans-serif;
            color: #1e293b;
        }

        .navbar-custom {
            background: linear-gradient(135deg, #00324d, #001f31);
            box-shadow: 0 4px 20px rgba(0,0,0,.15);
        }

        .hero-card {
            background: linear-gradient(
                135deg,
                rgba(57,169,0,.08),
                rgba(0,50,77,.05)
            );
            border: 1px solid rgba(57,169,0,.2);
            border-radius: 20px;
        }

        .card-creative {
            border: none;
            border-radius: 18px;
            box-shadow: 0 10px 30px rgba(0,0,0,.05);
            background: white;
        }

        .card-creative:hover {
            box-shadow: 0 12px 32px rgba(0,0,0,.08);
        }

        .badge-sena {
            background: var(--sena-green);
            color: white;
            padding: 6px 14px;
            border-radius: 50px;
        }

        .btn-creative {
            background: linear-gradient(135deg, #39a900, #00843d);
            color: white;
            border: none;
            border-radius: 12px;
            padding: 12px 24px;
            font-weight: bold;
        }

        .btn-creative:hover {
            background: #00843d;
            color: white;
        }

        .kpi-card {
            border-left: 5px solid var(--sena-green);
        }

        @media print {
            nav, .no-print, footer {
                display: none !important;
            }
        }
    </style>
</head>

<body>
<nav class="navbar navbar-expand-lg navbar-dark navbar-custom py-3">
    <div class="container">
        <a class="navbar-brand fw-bold" href="/">
            <i class="bi bi-building-fill-gear text-warning"></i>
            Colegio Integrado Camilo Torres | SENA GAES 5
        </a>

        <div class="navbar-nav ms-auto">
            <a class="nav-link text-white" href="/">Inicio</a>
            <a class="nav-link text-white" href="/registro">Encuesta</a>
            <a class="btn btn-warning fw-bold" href="/login">Panel Docente</a>
        </div>
    </div>
</nav>

<div class="container my-5">
    {% block content %}{% endblock %}
</div>

<footer class="text-center py-4 text-muted border-top bg-white">
    <small>© 2026 Colegio Integrado Camilo Torres | SENA GAES 5</small>
</footer>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""


@app.route("/")
def index():
    contenido = """
    <div class="row justify-content-center animate__animated animate__fadeIn">
        <div class="col-lg-10">
            <div class="hero-card p-5 text-center shadow-sm">

                <span class="badge-sena">
                    San Vicente de Chucurí
                </span>

                <h1 class="display-5 fw-bold mt-3">
                    Diagnóstico y Comparativo de Rendimiento Académico
                </h1>

                <h4 class="text-success fw-bold mb-4">
                    Colegio Integrado Camilo Torres
                </h4>

                <p class="lead text-secondary">
                    Plataforma para analizar el rendimiento académico,
                    los hábitos de estudio y las causas relacionadas
                    con las dificultades escolares.
                </p>

                <div class="row g-4 my-4">
                    <div class="col-md-4">
                        <div class="card card-creative p-4 h-100">
                            <i class="bi bi-journal-text text-success fs-1"></i>
                            <h5 class="fw-bold mt-2">Encuesta</h5>
                            <p>Registro de información académica.</p>
                        </div>
                    </div>

                    <div class="col-md-4">
                        <div class="card card-creative p-4 h-100">
                            <i class="bi bi-bar-chart text-warning fs-1"></i>
                            <h5 class="fw-bold mt-2">Gráficas</h5>
                            <p>Comparación de los resultados registrados.</p>
                        </div>
                    </div>

                    <div class="col-md-4">
                        <div class="card card-creative p-4 h-100">
                            <i class="bi bi-clipboard-data text-danger fs-1"></i>
                            <h5 class="fw-bold mt-2">Diagnóstico</h5>
                            <p>Consulta de los datos del sistema.</p>
                        </div>
                    </div>
                </div>

                <a href="/registro" class="btn btn-creative btn-lg m-2">
                    <i class="bi bi-pencil-square"></i>
                    Diligenciar encuesta
                </a>

                <a href="/login" class="btn btn-outline-dark btn-lg m-2">
                    <i class="bi bi-speedometer2"></i>
                    Panel docente
                </a>
            </div>
        </div>
    </div>
    """

    return render_template_string(
        HTML_LAYOUT.replace(
            "{% block content %}{% endblock %}", contenido
        )
    )


@app.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        documento = request.form.get("documento", "").strip()
        ficha = request.form.get("ficha", "").strip()
        estado = request.form.get("estado_rendimiento", "")
        motivo = request.form.get("motivo", "")
        horas = request.form.get("horas", "")

        try:
            materias = int(request.form.get("materias", "0"))
        except ValueError:
            materias = 0

        if not nombre or not documento or not ficha:
            return "Completa el nombre, documento y ficha.", 400

        if estado not in ["Buen Rendimiento", "Bajo Rendimiento"]:
            return "Selecciona un estado de rendimiento válido.", 400

        if materias < 0 or materias > 15:
            return "El número de materias debe estar entre 0 y 15.", 400

        conn = get_db_connection()

        conn.execute("""
            INSERT INTO estudiantes
            (nombre, documento, ficha, estado_rendimiento,
             motivo, horas_estudio, materias_reprobadas, origen)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'Real')
        """, (
            nombre,
            documento,
            ficha,
            estado,
            motivo,
            horas,
            materias
        ))

        conn.commit()
        conn.close()

        return redirect(url_for("admin"))

    contenido = """
    <div class="row justify-content-center">
        <div class="col-lg-8">
            <div class="card card-creative p-4 p-md-5">

                <h2 class="fw-bold mb-2">
                    <i class="bi bi-card-checklist text-success"></i>
                    Encuesta de Rendimiento Académico
                </h2>

                <p class="text-muted">
                    Colegio Integrado Camilo Torres
                </p>

                <form method="POST">
                    <div class="row g-3">

                        <div class="col-md-6">
                            <label class="form-label fw-bold">
                                Nombre completo
                            </label>
                            <input name="nombre"
                                   class="form-control"
                                   required maxlength="100">
                        </div>

                        <div class="col-md-6">
                            <label class="form-label fw-bold">
                                Documento de identidad
                            </label>
                            <input name="documento"
                                   class="form-control"
                                   required maxlength="30">
                        </div>

                        <div class="col-md-6">
                            <label class="form-label fw-bold">
                                Ficha / Grupo
                            </label>
                            <input name="ficha"
                                   class="form-control"
                                   value="3157141"
                                   required maxlength="30">
                        </div>

                        <div class="col-md-6">
                            <label class="form-label fw-bold">
                                Rendimiento académico
                            </label>
                            <select name="estado_rendimiento"
                                    class="form-select" required>
                                <option value="Buen Rendimiento">
                                    Buen Rendimiento
                                </option>
                                <option value="Bajo Rendimiento" selected>
                                    Bajo Rendimiento
                                </option>
                            </select>
                        </div>

                        <div class="col-md-6">
                            <label class="form-label fw-bold">
                                Horas de estudio semanales
                            </label>
                            <select name="horas"
                                    class="form-select" required>
                                <option>0-1 horas</option>
                                <option selected>1-3 horas</option>
                                <option>3-5 horas</option>
                                <option>+5 horas</option>
                            </select>
                        </div>

                        <div class="col-md-6">
                            <label class="form-label fw-bold">
                                Materias reprobadas
                            </label>
                            <input type="number"
                                   name="materias"
                                   class="form-control"
                                   min="0" max="15"
                                   value="1" required>
                        </div>

                        <div class="col-12">
                            <label class="form-label fw-bold">
                                Causa u observación
                            </label>
                            <select name="motivo"
                                    class="form-select" required>
                                <option value="Falta de Hábitos de Estudio">
                                    Falta de hábitos de estudio
                                </option>
                                <option value="Ninguno / Excelente Desempeño">
                                    Ninguno / Excelente desempeño
                                </option>
                                <option value="Afectación Emocional / Personal">
                                    Afectación emocional o personal
                                </option>
                                <option value="Incidencia Docente / Metodología">
                                    Metodología de enseñanza
                                </option>
                                <option value="Dificultad Técnica / Herramientas">
                                    Dificultad técnica o herramientas digitales
                                </option>
                            </select>
                        </div>
                    </div>

                    <button class="btn btn-creative w-100 mt-4" type="submit">
                        <i class="bi bi-send-check"></i>
                        Registrar diagnóstico
                    </button>
                </form>
            </div>
        </div>
    </div>
    """

    return render_template_string(
        HTML_LAYOUT.replace(
            "{% block content %}{% endblock %}", contenido
        )
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    # Acceso demostrativo: no constituye autenticación segura.
    if request.method == "POST":
        return redirect(url_for("admin"))

    contenido = """
    <div class="row justify-content-center">
        <div class="col-md-5">
            <div class="card card-creative p-5 text-center">

                <i class="bi bi-shield-lock-fill text-success"
                   style="font-size:3rem"></i>

                <h3 class="fw-bold mt-3">Panel Docente</h3>

                <p class="text-muted">
                    Acceso de demostración para consultar los resultados.
                </p>

                <form method="POST">
                    <label class="form-label">Usuario</label>
                    <input name="user"
                           class="form-control mb-3"
                           value="admin" required>

                    <label class="form-label">Contraseña</label>
                    <input name="pass"
                           type="password"
                           class="form-control mb-3"
                           required>

                    <button class="btn btn-creative w-100">
                        Entrar al panel
                    </button>
                </form>
            </div>
        </div>
    </div>
    """

    return render_template_string(
        HTML_LAYOUT.replace(
            "{% block content %}{% endblock %}", contenido
        )
    )


@app.route("/admin")
def admin():
    conn = get_db_connection()

    estudiantes = conn.execute("""
        SELECT * FROM estudiantes ORDER BY id DESC
    """).fetchall()

    fichas_query = conn.execute("""
        SELECT ficha,
            SUM(
                CASE
                    WHEN estado_rendimiento = 'Buen Rendimiento'
                    THEN 1 ELSE 0
                END
            ) AS buen,
            SUM(
                CASE
                    WHEN estado_rendimiento = 'Bajo Rendimiento'
                    THEN 1 ELSE 0
                END
            ) AS bajo
        FROM estudiantes
        GROUP BY ficha
        ORDER BY ficha
    """).fetchall()

    motivos_query = conn.execute("""
        SELECT motivo, COUNT(*) AS cantidad
        FROM estudiantes
        GROUP BY motivo
    """).fetchall()

    conn.close()

    labels_fichas = [r["ficha"] for r in fichas_query]
    datos_buen = [r["buen"] for r in fichas_query]
    datos_bajo = [r["bajo"] for r in fichas_query]

    labels_motivos = [r["motivo"] for r in motivos_query]
    datos_motivos = [r["cantidad"] for r in motivos_query]

    total = len(estudiantes)
    total_buen = sum(datos_buen)
    total_bajo = sum(datos_bajo)

    filas = ""

    for e in estudiantes:
        estado = e["estado_rendimiento"] or "Bajo Rendimiento"

        badge = (
            "bg-success"
            if estado == "Buen Rendimiento"
            else "bg-danger"
        )

        filas += f"""
        <tr>
            <td>{escape(str(e['nombre']))}</td>
            <td>{escape(str(e['documento']))}</td>
            <td>
                <span class="badge bg-secondary">
                    {escape(str(e['ficha']))}
                </span>
            </td>
            <td>
                <span class="badge {badge}">
                    {escape(estado)}
                </span>
            </td>
            <td>{escape(str(e['motivo']))}</td>
            <td>{escape(str(e['horas_estudio']))}</td>
            <td class="text-center">
                {e['materias_reprobadas']}
            </td>
        </tr>
        """

    colores = [
        "#39a900",
        "#ffc107",
        "#dc3545",
        "#0dcaf0",
        "#6f42c1",
        "#fd7e14",
        "#20c997",
        "#6610f2"
    ]

    json_fichas = json.dumps(labels_fichas, ensure_ascii=False)
    json_buen = json.dumps(datos_buen)
    json_bajo = json.dumps(datos_bajo)
    json_motivos = json.dumps(labels_motivos, ensure_ascii=False)
    json_cantidades = json.dumps(datos_motivos)
    json_colores = json.dumps(colores)

    contenido = f"""
    <div class="animate__animated animate__fadeIn">

        <div class="d-flex flex-wrap justify-content-between
                    align-items-center mb-4">
            <div>
                <h2 class="fw-bold">
                    <i class="bi bi-speedometer2 text-success"></i>
                    Panel de Rendimiento Académico
                </h2>

                <p class="text-muted">
                    Colegio Integrado Camilo Torres - SENA GAES 5
                </p>
            </div>

            <button onclick="window.print()"
                    class="btn btn-outline-dark no-print">
                <i class="bi bi-printer"></i>
                Imprimir informe
            </button>
        </div>

        <div class="row g-4 mb-4">

            <div class="col-md-4">
                <div class="card card-creative p-4 kpi-card border-primary">
                    <small class="text-muted fw-bold">
                        TOTAL DE REGISTROS
                    </small>
                    <h2 class="display-5 fw-bold">{total}</h2>
                    <span class="text-primary">Registrados</span>
                </div>
            </div>

            <div class="col-md-4">
                <div class="card card-creative p-4 kpi-card border-success">
                    <small class="text-muted fw-bold">
                        BUEN RENDIMIENTO
                    </small>
                    <h2 class="display-5 fw-bold text-success">
                        {total_buen}
                    </h2>
                    <span class="text-success">Buen desempeño</span>
                </div>
            </div>

            <div class="col-md-4">
                <div class="card card-creative p-4 kpi-card border-danger">
                    <small class="text-muted fw-bold">
                        BAJO RENDIMIENTO
                    </small>
                    <h2 class="display-5 fw-bold text-danger">
                        {total_bajo}
                    </h2>
                    <span class="text-danger">En riesgo académico</span>
                </div>
            </div>

        </div>

        <div class="row g-4 mb-4">

            <div class="col-lg-7">
                <div class="card card-creative p-4 h-100">
                    <h5 class="fw-bold">
                        Rendimiento por ficha
                    </h5>

                    <div style="height:320px">
                        <canvas id="fichasChart"></canvas>
                    </div>
                </div>
            </div>

            <div class="col-lg-5">
                <div class="card card-creative p-4 h-100">
                    <h5 class="fw-bold">
                        Causas registradas
                    </h5>

                    <div style="height:320px">
                        <canvas id="motivosChart"></canvas>
                    </div>
                </div>
            </div>

        </div>

        <div class="card card-creative p-4">

            <div class="d-flex flex-wrap justify-content-between
                        align-items-center mb-3">
                <h5 class="fw-bold mb-0">
                    <i class="bi bi-table"></i>
                    Estudiantes registrados
                </h5>

                <span class="badge bg-success">
                    {total} registros
                </span>
            </div>

            <div class="table-responsive">
                <table class="table table-hover align-middle">

                    <thead class="table-dark">
                        <tr>
                            <th>Nombre</th>
                            <th>Documento</th>
                            <th>Ficha</th>
                            <th>Rendimiento</th>
                            <th>Causa</th>
                            <th>Horas de estudio</th>
                            <th>Reprobadas</th>
                        </tr>
                    </thead>

                    <tbody>
                        {filas}
                    </tbody>

                </table>
            </div>

            <a href="/registro"
               class="btn btn-creative no-print">
                <i class="bi bi-plus-circle"></i>
                Registrar otra respuesta
            </a>

        </div>
    </div>

    <script>
        const labelsFichas = {json_fichas};
        const datosBuen = {json_buen};
        const datosBajo = {json_bajo};

        const labelsMotivos = {json_motivos};
        const datosMotivos = {json_cantidades};
        const colores = {json_colores};

        new Chart(document.getElementById("fichasChart"), {{
            type: "bar",

            data: {{
                labels: labelsFichas,

                datasets: [
                    {{
                        label: "Buen rendimiento",
                        data: datosBuen,
                        backgroundColor: "#39a900",
                        borderRadius: 6
                    }},
                    {{
                        label: "Bajo rendimiento",
                        data: datosBajo,
                        backgroundColor: "#dc3545",
                        borderRadius: 6
                    }}
                ]
            }},

            options: {{
                responsive: true,
                maintainAspectRatio: false,

                scales: {{
                    y: {{
                        beginAtZero: true,
                        ticks: {{
                            stepSize: 1
                        }}
                    }}
                }}
            }}
        }});

        new Chart(document.getElementById("motivosChart"), {{
            type: "doughnut",

            data: {{
                labels: labelsMotivos,

                datasets: [{{
                    data: datosMotivos,

                    backgroundColor: labelsMotivos.map(
                        (_, i) => colores[i % colores.length]
                    ),

                    borderWidth: 2
                }}]
            }},

            options: {{
                responsive: true,
                maintainAspectRatio: false,

                plugins: {{
                    legend: {{
                        position: "bottom"
                    }}
                }}
            }}
        }});
    </script>
    """

    return render_template_string(
        HTML_LAYOUT.replace(
            "{% block content %}{% endblock %}", contenido
        )
    )


if __name__ == "__main__":
    app.run(debug=True)
