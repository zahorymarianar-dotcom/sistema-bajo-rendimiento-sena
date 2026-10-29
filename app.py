from flask import Flask, request, redirect, url_for, render_template_string
import sqlite3
import json
from html import escape
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "sena_proyecto_secret")

DATABASE = os.environ.get("DATABASE_PATH", "database.db")


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
            origen TEXT DEFAULT 'Real',
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

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

        .proyecto-hero {
            background: linear-gradient(135deg, #00324d, #006b45);
            color: white;
            padding: 40px 25px;
            border-radius: 22px;
            text-align: center;
        }

        .proyecto-card {
            background: white;
            border-radius: 20px;
            padding: 25px;
            box-shadow: 0 8px 25px rgba(0,0,0,.08);
            height: 100%;
        }

        .foto-integrante {
            width: 175px;
            height: 175px;
            object-fit: cover;
            object-position: center;
            border-radius: 50%;
            border: 5px solid #39a900;
            margin-bottom: 18px;
        }

        .logo-colegio {
            width: 150px;
            height: 150px;
            object-fit: contain;
            background: white;
            border-radius: 50%;
            padding: 5px;
            margin-bottom: 18px;
        }

        .titulo-verde {
            color: #00843d;
            font-weight: bold;
        }

        .aporte {
            background: #f0f8ec;
            border-left: 5px solid #39a900;
            padding: 15px;
            border-radius: 10px;
            text-align: left;
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

        <button class="navbar-toggler" type="button"
                data-bs-toggle="collapse"
                data-bs-target="#menuPrincipal">
            <span class="navbar-toggler-icon"></span>
        </button>

        <div class="collapse navbar-collapse" id="menuPrincipal">
            <div class="navbar-nav ms-auto">
                <a class="nav-link text-white" href="/">Inicio</a>
                <a class="nav-link text-white" href="/proyecto">Nuestro proyecto</a>
                <a class="nav-link text-white" href="/registro">Encuesta</a>
                <a class="btn btn-warning fw-bold ms-lg-2" href="/login">
                    Panel Docente
                </a>
            </div>
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


def mostrar_pagina(contenido):
    return render_template_string(
        HTML_LAYOUT.replace(
            "{% block content %}{% endblock %}",
            contenido
        )
    )


@app.route("/")
def index():
    contenido = """
    <div class="row justify-content-center animate__animated animate__fadeIn">
        <div class="col-lg-10">

            <div class="hero-card p-5 text-center shadow-sm">

                <span class="badge-sena">San Vicente de Chucurí</span>

                <h1 class="display-5 fw-bold mt-3">
                    Diagnóstico y Comparativo de Rendimiento Académico
                </h1>

                <h4 class="text-success fw-bold mb-4">
                    Colegio Integrado Camilo Torres
                </h4>

                <p class="lead text-secondary">
                    Plataforma para analizar el rendimiento académico,
                    los hábitos de estudio y algunas dificultades que
                    pueden afectar el aprendizaje de los estudiantes.
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
                            <p>Visualización de los datos registrados.</p>
                        </div>
                    </div>

                    <div class="col-md-4">
                        <div class="card card-creative p-4 h-100">
                            <i class="bi bi-clipboard-data text-danger fs-1"></i>
                            <h5 class="fw-bold mt-2">Diagnóstico</h5>
                            <p>Consulta de la información recopilada.</p>
                        </div>
                    </div>

                </div>

                <a href="/proyecto" class="btn btn-creative btn-lg m-2">
                    <i class="bi bi-people-fill"></i>
                    Conoce nuestro proyecto
                </a>

                <a href="/registro" class="btn btn-outline-success btn-lg m-2">
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

    return mostrar_pagina(contenido)


@app.route("/proyecto")
def proyecto():
    contenido = """
    <div class="animate__animated animate__fadeIn">

        <section class="proyecto-hero mb-4">

            <img src="{{ url_for('static', filename='colegio.png') }}"
                 alt="Escudo del Colegio Integrado Camilo Torres"
                 class="logo-colegio">

            <h1 class="fw-bold">Nuestro proyecto</h1>

            <h4>Diagnóstico del bajo rendimiento académico de grado décimo</h4>

            <p class="mt-3 mb-0">
                Colegio Integrado Camilo Torres
                <br>
                San Vicente de Chucurí, Santander
            </p>

        </section>

        <section class="proyecto-card mb-4">

            <h2 class="titulo-verde">
                <i class="bi bi-book-half"></i>
                ¿De qué trata nuestro proyecto?
            </h2>

            <p class="mt-3">
                Nuestro proyecto busca abordar el bajo rendimiento académico
                de los estudiantes de grado décimo del Colegio Integrado
                Camilo Torres. Para ello, desarrollamos una página web que
                permite registrar información relacionada con el rendimiento
                académico, los hábitos de estudio y algunas dificultades que
                pueden influir en el aprendizaje.
            </p>

            <p>
                La plataforma organiza la información en una tabla y la
                representa mediante gráficas que facilitan la interpretación
                de los datos. De esta manera, buscamos contar con una
                herramienta de apoyo para identificar situaciones que
                requieren atención y contribuir a la búsqueda de estrategias
                de mejoramiento académico.
            </p>

            <p class="mb-0">
                Este proyecto integra conocimientos de programación y
                análisis de datos para proponer una solución tecnológica
                a una situación del entorno escolar.
            </p>

        </section>

        <section class="mb-4">

            <h2 class="text-center fw-bold mb-4">
                Nuestro equipo de trabajo
            </h2>

            <div class="row g-4">

                <div class="col-md-6">
                    <div class="proyecto-card text-center">

                        <img src="{{ url_for('static', filename='yopis.png') }}"
                             alt="Fotografía de Zahory Mariana Rueda Bueno"
                             class="foto-integrante">

                        <h4 class="titulo-verde">
                            Zahory Mariana Rueda Bueno
                        </h4>

                        <p class="text-muted">
                            Desarrollo de la página web
                        </p>

                        <div class="aporte">
                            <strong>Mi aporte al proyecto:</strong>

                            <p class="mb-0 mt-2">
                                Me encargué del desarrollo de la página web,
                                trabajando en su estructura, diseño y
                                funcionamiento. También trabajé en el
                                formulario de registro, la organización de
                                los datos y la visualización de los resultados
                                mediante gráficas.
                            </p>
                        </div>

                    </div>
                </div>

                <div class="col-md-6">
                    <div class="proyecto-card text-center">

                        <img src="{{ url_for('static', filename='peña.png') }}"
                             alt="Fotografía de Elías Josué Peña Ballena"
                             class="foto-integrante">

                        <h4 class="titulo-verde">
                            Elías Josué Peña Ballena
                        </h4>

                        <p class="text-muted">
                            Elaboración de bitácoras y evidencias
                        </p>

                        <div class="aporte">
                            <strong>Su aporte al proyecto:</strong>

                            <p class="mb-0 mt-2">
                                Se encargó de la elaboración de las bitácoras
                                y de la organización de las evidencias del
                                proceso. Su trabajo permitió documentar las
                                actividades realizadas y los avances del
                                proyecto durante su desarrollo.
                            </p>
                        </div>

                    </div>
                </div>

            </div>

        </section>

        <section class="proyecto-card text-center mb-4">

            <h3 class="titulo-verde">Nuestro propósito</h3>

            <p>
                Demostrar cómo la tecnología y el análisis de datos pueden
                ayudar a comprender una problemática escolar y apoyar la
                búsqueda de posibles soluciones.
            </p>

            <p class="mb-0">
                Como equipo, aportamos habilidades diferentes que se
                complementan para desarrollar y documentar nuestra propuesta.
            </p>

        </section>

        <div class="text-center mb-4">
            <a href="/" class="btn btn-creative">
                <i class="bi bi-house-fill"></i>
                Volver al inicio
            </a>
        </div>

    </div>
    """

    return mostrar_pagina(contenido)


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
            return "Selecciona un rendimiento válido.", 400

        if materias < 0 or materias > 15:
            return "Las materias deben estar entre 0 y 15.", 400

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
                            <input name="nombre" class="form-control"
                                   required maxlength="100">
                        </div>

                        <div class="col-md-6">
                            <label class="form-label fw-bold">
                                Documento de identidad
                            </label>
                            <input name="documento" class="form-control"
                                   required maxlength="30">
                        </div>

                        <div class="col-md-6">
                            <label class="form-label fw-bold">
                                Ficha / Grupo
                            </label>
                            <input name="ficha" class="form-control"
                                   value="3157141" required maxlength="30">
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
                            <select name="horas" class="form-select" required>
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
                            <input type="number" name="materias"
                                   class="form-control" min="0" max="15"
                                   value="1" required>
                        </div>

                        <div class="col-12">
                            <label class="form-label fw-bold">
                                Causa u observación
                            </label>
                            <select name="motivo" class="form-select" required>
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
                        Registrar respuesta
                    </button>

                </form>
            </div>
        </div>
    </div>
    """

    return mostrar_pagina(contenido)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        return redirect(url_for("admin"))

    contenido = """
    <div class="row justify-content-center">
        <div class="col-md-5">

            <div class="card card-creative p-5 text-center">

                <i class="bi bi-speedometer2 text-success"
                   style="font-size:3rem"></i>

                <h3 class="fw-bold mt-3">Panel Docente</h3>

                <p class="text-muted">
                    Acceso de demostración.
                </p>

                <form method="POST">

                    <label class="form-label">Usuario</label>
                    <input name="user" class="form-control mb-3"
                           value="admin" required>

                    <label class="form-label">Contraseña</label>
                    <input name="pass" type="password"
                           class="form-control mb-3" required>

                    <button class="btn btn-creative w-100">
                        Entrar al panel
                    </button>

                </form>

            </div>
        </div>
    </div>
    """

    return mostrar_pagina(contenido)


@app.route("/admin")
def admin():
    conn = get_db_connection()

    estudiantes = conn.execute("""
        SELECT * FROM estudiantes ORDER BY id DESC
    """).fetchall()

    fichas_query = conn.execute("""
        SELECT ficha,
            SUM(CASE
                WHEN estado_rendimiento = 'Buen Rendimiento'
                THEN 1 ELSE 0
            END) AS buen,
            SUM(CASE
                WHEN estado_rendimiento = 'Bajo Rendimiento'
                THEN 1 ELSE 0
            END) AS bajo
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

    total = len(estudiantes)

    total_buen = sum(r["buen"] or 0 for r in fichas_query)
    total_bajo = sum(r["bajo"] or 0 for r in fichas_query)

    labels_fichas = [r["ficha"] for r in fichas_query]
    datos_buen = [r["buen"] or 0 for r in fichas_query]
    datos_bajo = [r["bajo"] or 0 for r in fichas_query]

    labels_motivos = [r["motivo"] for r in motivos_query]
    datos_motivos = [r["cantidad"] for r in motivos_query]

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
            <td>{escape(str(e["nombre"]))}</td>
            <td>{escape(str(e["documento"]))}</td>
            <td>{escape(str(e["ficha"]))}</td>
            <td>
                <span class="badge {badge}">
                    {escape(estado)}
                </span>
            </td>
            <td>{escape(str(e["motivo"] or ""))}</td>
            <td>{escape(str(e["horas_estudio"] or ""))}</td>
            <td class="text-center">
                {e["materias_reprobadas"] or 0}
            </td>
        </tr>
        """

    colores = [
        "#39a900", "#ffc107", "#dc3545", "#0dcaf0",
        "#6f42c1", "#fd7e14", "#20c997", "#6610f2"
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
                <div class="card card-creative p-4 kpi-card">
                    <small class="text-muted fw-bold">
                        TOTAL DE REGISTROS
                    </small>
                    <h2 class="display-5 fw-bold">{total}</h2>
                    <span class="text-primary">Registros guardados</span>
                </div>
            </div>

            <div class="col-md-4">
                <div class="card card-creative p-4 kpi-card">
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
                <div class="card card-creative p-4 kpi-card">
                    <small class="text-muted fw-bold">
                        BAJO RENDIMIENTO
                    </small>
                    <h2 class="display-5 fw-bold text-danger">
                        {total_bajo}
                    </h2>
                    <span class="text-danger">Requieren atención</span>
                </div>
            </div>

        </div>

        <div class="row g-4 mb-4">

            <div class="col-lg-7">
                <div class="card card-creative p-4 h-100">
                    <h5 class="fw-bold">Rendimiento por ficha</h5>
                    <div style="height:320px">
                        <canvas id="fichasChart"></canvas>
                    </div>
                </div>
            </div>

            <div class="col-lg-5">
                <div class="card card-creative p-4 h-100">
                    <h5 class="fw-bold">Causas registradas</h5>
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

                <span class="badge bg-success">{total} registros</span>

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

            <a href="/registro" class="btn btn-creative no-print">
                <i class="bi bi-plus-circle"></i>
                Registrar otra respuesta
            </a>

            <a href="/proyecto"
               class="btn btn-outline-success mt-2 no-print">
                <i class="bi bi-people-fill"></i>
                Ver nuestro proyecto
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
                        ticks: {{ stepSize: 1 }}
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
                    legend: {{ position: "bottom" }}
                }}
            }}
        }});
    </script>
    """

    return mostrar_pagina(contenido)


if __name__ == "__main__":
    app.run(debug=True)
