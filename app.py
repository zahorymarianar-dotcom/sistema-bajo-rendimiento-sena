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
