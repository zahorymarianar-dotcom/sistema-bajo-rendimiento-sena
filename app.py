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
                                <th>Tipo de dato</th>
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
