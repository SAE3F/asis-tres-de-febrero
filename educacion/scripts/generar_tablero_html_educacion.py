# -*- coding: utf-8 -*-
"""
generar_tablero_html_educacion.py
Generador del Tablero Web Interactivo de Educación (ASIS-Educación)
para la Municipalidad de Tres de Febrero (06840), autónomo y auto-contenido en educacion/index.html.
"""

import os
import sys
import json
import base64

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

def get_base64_file(filepath):
    if not os.path.exists(filepath):
        return ""
    with open(filepath, "rb") as f:
        return base64.b64encode(f.read()).decode('utf-8')

def generar_tablero_educacion():
    # Directorios base
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # educacion/
    root_dir = os.path.dirname(base_dir) # salud tres de febrero/
    salidas_dir = os.path.join(base_dir, 'salidas')
    datos_dir = os.path.join(root_dir, 'datos')
    
    html_out = os.path.join(base_dir, 'index.html')
    
    print("--- GENERANDO TABLERO HTML INTERACTIVO DE EDUCACIÓN (ASIS-3F) ---")
    
    # 1. Cargar GeoJSON exacto de los 457 radios censales del Partido
    geojson_path = os.path.join(datos_dir, 'radios_censales_3f.geojson')
    if os.path.exists(geojson_path):
        with open(geojson_path, 'r', encoding='utf-8') as gf:
            geojson_data = json.load(gf)
    else:
        geojson_data = {"type": "FeatureCollection", "features": []}
    geojson_json_str = json.dumps(geojson_data, ensure_ascii=False)
    
    # 2. Cargar Logo Municipal (logo.png) desde el directorio raíz
    logo_path = os.path.join(root_dir, 'logo.png')
    b64_logo = get_base64_file(logo_path)
    
    # 3. Cargar Documento Word de Educación (.docx) para descarga en Base64
    docx_path = os.path.join(salidas_dir, 'informe_situacion_educativa_3f.docx')
    b64_docx = get_base64_file(docx_path)
    print(f" -> Archivo Word de Educación convertido a Base64 ({len(b64_docx)} caracteres)")
    
    # 4. Cargar Imágenes PNG de Gráficos de Educación a Base64
    img_names = [
        'grafico_asistencia_por_edad_3f.png',
        'grafico_nivel_educativo_3f_vs_gba.png',
        'grafico_brecha_digital_tic_3f.png',
        'grafico_distribucion_jardines_localidades.png'
    ]
    b64_imgs = {}
    for nom in img_names:
        path_sal = os.path.join(salidas_dir, nom)
        b64_imgs[nom] = get_base64_file(path_sal) if os.path.exists(path_sal) else ""

    print(f" -> Gráficos PNG de educación convertidos a Base64: {sum(1 for v in b64_imgs.values() if v)}")

    html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0, user-scalable=yes">
    <title>Educación — Municipalidad de Tres de Febrero (ASIS y Censo 2022)</title>
    <!-- Google Fonts: Montserrat & Inter -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <!-- Chart.js -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <!-- Leaflet SIG -->
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <style>
        :root {{
            /* Paleta Oficial Municipalidad de Tres de Febrero */
            --azul-primario: #163C68;
            --azul-oscuro: #0E2A49;
            --azul-suave: #B8D0EB;
            --azul-claro: #E0EEFF;
            --naranja: #F69321;
            --naranja-oscuro: #DB7A0B;
            --naranja-suave: #F6BF80;
            --naranja-claro: #F6E6D4;
            /* Neutrals */
            --neutro-900: #000D1D;
            --neutro-700: #2F4054;
            --neutro-500: #B1B7BE;
            --neutro-300: #E5E5E5;
            --neutro-100: #F8F8F8;
            --neutro-0: #FDFDFD;
            /* System */
            --verde: #13B423;
            --rojo: #DB3D3D;
            --amarillo: #E8A700;
            --azul-info: #3B93F7;
            /* Shadows & Radius */
            --shadow-sm: 0 1px 3px rgba(0, 13, 29, 0.08);
            --shadow-md: 0 4px 12px rgba(0, 13, 29, 0.1);
            --shadow-lg: 0 8px 30px rgba(0, 13, 29, 0.12);
            --shadow-xl: 0 16px 48px rgba(0, 13, 29, 0.14);
            --radius-sm: 6px;
            --radius-md: 10px;
            --radius-lg: 16px;
            --radius-xl: 24px;
        }}

        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Montserrat', sans-serif;
            color: var(--neutro-900);
            background: var(--neutro-100);
            -webkit-font-smoothing: antialiased;
            overflow-x: hidden;
        }}

        /* TOPBAR & NAVBAR */
        .topbar {{ background: var(--azul-primario); height: 5px; width: 100%; }}
        .navbar {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 14px 48px;
            background: #fff;
            border-bottom: 1px solid var(--neutro-300);
            position: sticky;
            top: 0;
            z-index: 1000;
            box-shadow: var(--shadow-sm);
        }}
        .navbar-brand {{ display: flex; align-items: center; gap: 14px; }}
        .logo-3f {{ width: 48px; height: 48px; border-radius: 8px; overflow: hidden; flex-shrink: 0; display: flex; align-items: center; justify-content: center; background: #fff; border: 1px solid var(--neutro-300); }}
        .logo-3f img {{ width: 100%; height: 100%; object-fit: contain; }}
        .brand-text strong {{ display: block; font-size: 17px; font-weight: 800; color: var(--azul-primario); letter-spacing: -0.3px; }}
        .brand-text small {{ font-size: 12px; color: var(--neutro-700); font-weight: 500; }}
        
        .nav-actions {{ display: flex; align-items: center; gap: 12px; }}
        .btn-naranja {{
            background: var(--naranja);
            color: #fff;
            padding: 12px 22px;
            border-radius: var(--radius-sm);
            font-size: 13.5px;
            font-weight: 700;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            transition: all 0.2s;
            border: none;
            cursor: pointer;
            box-shadow: 0 4px 10px rgba(246, 147, 33, 0.3);
        }}
        .btn-naranja:hover {{ background: var(--naranja-oscuro); transform: translateY(-1px); }}

        /* HERO SECTION */
        .hero {{
            background: linear-gradient(135deg, var(--azul-oscuro) 0%, var(--azul-primario) 100%);
            color: #fff;
            padding: 40px 48px;
            border-bottom: 4px solid var(--naranja);
            margin-bottom: 30px;
            position: relative;
        }}
        .hero h1 {{ font-size: 32px; font-weight: 800; margin-bottom: 10px; line-height: 1.2; letter-spacing: -0.5px; }}
        .hero p {{ font-size: 15px; color: var(--azul-suave); max-width: 900px; line-height: 1.6; font-family: 'Inter', sans-serif; }}

        /* TABS NAV */
        .tabs-nav {{
            display: flex;
            gap: 4px;
            padding: 0 48px;
            background: #fff;
            border-bottom: 2px solid var(--neutro-300);
            overflow-x: auto;
            scrollbar-width: none;
        }}
        .tabs-nav::-webkit-scrollbar {{ display: none; }}
        .tab-btn {{
            padding: 15px 24px;
            font-size: 14px;
            font-weight: 700;
            color: var(--neutro-700);
            background: none;
            border: none;
            cursor: pointer;
            font-family: 'Montserrat', sans-serif;
            border-bottom: 3px solid transparent;
            margin-bottom: -2px;
            transition: all 0.2s;
            white-space: nowrap;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .tab-btn:hover {{ color: var(--azul-primario); }}
        .tab-btn.active {{ color: var(--azul-primario); border-bottom-color: var(--naranja); background: var(--azul-claro); border-radius: var(--radius-sm) var(--radius-sm) 0 0; }}

        /* MAIN CONTAINER */
        .main-container {{ max-width: 1400px; margin: 0 auto; padding: 30px 48px; }}
        .tab-pane {{ display: none; animation: fadeIn 0.35s ease; }}
        .tab-pane.active {{ display: block; }}
        @keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(6px); }} to {{ opacity: 1; transform: translateY(0); }} }}

        /* GRIDS & CARDS */
        .grid-4 {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 30px; }}
        .grid-2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 24px; margin-bottom: 30px; }}
        
        .kpi-card {{
            background: #fff;
            border-radius: var(--radius-lg);
            padding: 24px;
            border: 1.5px solid var(--neutro-300);
            box-shadow: var(--shadow-sm);
            transition: transform 0.2s, box-shadow 0.2s;
            position: relative;
            overflow: hidden;
        }}
        .kpi-card::before {{ content: ''; position: absolute; top: 0; left: 0; width: 6px; height: 100%; background: var(--azul-primario); }}
        .kpi-card.orange::before {{ background: var(--naranja); }}
        .kpi-card.green::before {{ background: var(--verde); }}
        .kpi-card:hover {{ transform: translateY(-3px); box-shadow: var(--shadow-md); }}
        .kpi-title {{ font-size: 13px; font-weight: 700; text-transform: uppercase; color: var(--neutro-700); margin-bottom: 8px; font-family: 'Inter', sans-serif; letter-spacing: 0.5px; }}
        .kpi-val {{ font-size: 32px; font-weight: 800; color: var(--azul-primario); line-height: 1.1; margin-bottom: 6px; }}
        .kpi-sub {{ font-size: 12px; color: var(--neutro-700); font-family: 'Inter', sans-serif; }}

        .card-panel {{
            background: #fff;
            border-radius: var(--radius-lg);
            padding: 28px;
            border: 1.5px solid var(--neutro-300);
            box-shadow: var(--shadow-sm);
            margin-bottom: 24px;
        }}
        .card-panel h2 {{ font-size: 20px; font-weight: 800; color: var(--azul-primario); margin-bottom: 12px; display: flex; align-items: center; gap: 10px; }}
        .card-panel p.desc {{ font-size: 14px; color: var(--neutro-700); line-height: 1.6; margin-bottom: 20px; font-family: 'Inter', sans-serif; }}

        /* MAP CONTAINER */
        #mapa-leaflet-container {{ width: 100%; height: 580px; border-radius: var(--radius-md); border: 2px solid var(--neutro-300); box-shadow: var(--shadow-inner); z-index: 10; position: relative; }}
        .map-controls {{ display: flex; gap: 12px; margin-bottom: 16px; flex-wrap: wrap; align-items: center; justify-content: space-between; }}
        
        .btn-secundario {{
            background: var(--azul-claro);
            color: var(--azul-primario);
            border: 1.5px solid var(--azul-suave);
            padding: 10px 18px;
            border-radius: var(--radius-sm);
            font-size: 13px;
            font-weight: 700;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            transition: all 0.2s;
        }}
        .btn-secundario:hover {{ background: var(--azul-primario); color: #fff; }}

        /* DIRECTORY CARDS */
        .efectores-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }}
        .efector-card {{ background: #fff; border: 1.5px solid var(--neutro-300); border-radius: var(--radius-md); padding: 22px; transition: all 0.2s; display: flex; flex-direction: column; justify-content: space-between; }}
        .efector-card:hover {{ border-color: var(--naranja); box-shadow: var(--shadow-md); transform: translateY(-2px); }}
        .efector-tag {{ font-size: 11px; font-weight: 800; text-transform: uppercase; padding: 4px 10px; border-radius: 100px; background: var(--azul-claro); color: var(--azul-primario); display: inline-block; margin-bottom: 10px; font-family: 'Inter', sans-serif; }}
        .efector-tag.orange {{ background: var(--naranja-claro); color: var(--naranja-oscuro); }}
        .efector-tag.green {{ background: #DCFCE7; color: #166534; }}
        .efector-card h3 {{ font-size: 17px; font-weight: 700; color: var(--azul-primario); margin-bottom: 8px; }}
        .efector-card p {{ font-size: 13px; color: var(--neutro-700); line-height: 1.5; font-family: 'Inter', sans-serif; margin-bottom: 12px; }}
        .efector-footer {{ font-size: 12px; font-weight: 600; color: var(--naranja-oscuro); border-top: 1px solid var(--neutro-300); padding-top: 10px; margin-top: auto; display: flex; align-items: center; gap: 6px; }}

        /* PROGRAMAS LIST */
        .programas-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
        .prog-badge {{ background: var(--neutro-100); border-left: 4px solid var(--naranja); padding: 18px; border-radius: var(--radius-sm); border: 1px solid var(--neutro-300); }}
        .prog-badge h4 {{ font-size: 16px; font-weight: 700; color: var(--azul-primario); margin-bottom: 6px; }}
        .prog-badge p {{ font-size: 13.5px; color: var(--neutro-700); line-height: 1.6; font-family: 'Inter', sans-serif; }}

        /* FOOTER */
        footer {{ background: var(--azul-oscuro); color: #fff; padding: 40px 48px; margin-top: 60px; border-top: 4px solid var(--naranja); }}
        .footer-content {{ max-width: 1400px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 20px; }}
        .footer-content p.inst {{ font-size: 15px; font-weight: 700; margin-bottom: 4px; }}
        .footer-content p.sub {{ font-size: 13px; color: var(--azul-suave); font-family: 'Inter', sans-serif; }}

        /* MODAL PANTALLA COMPLETA MAPA */
        #mapa-modal-container {{
            display: none;
            position: fixed;
            top: 0; left: 0; width: 100vw; height: 100vh;
            background: rgba(0, 13, 29, 0.95);
            z-index: 99999;
            padding: 20px;
            flex-direction: column;
        }}
        #mapa-modal-container.active {{ display: flex; }}
        #mapa-fullscreen-leaflet {{ width: 100%; flex: 1; border-radius: var(--radius-md); border: 3px solid var(--naranja); }}
        .modal-header {{ display: flex; justify-content: space-between; align-items: center; color: #fff; margin-bottom: 12px; }}
        .modal-header h3 {{ font-size: 20px; font-weight: 700; color: var(--naranja); }}
        .btn-close-modal {{ background: var(--rojo); color: #fff; border: none; padding: 10px 20px; border-radius: var(--radius-sm); font-weight: 700; cursor: pointer; font-size: 14px; }}

        /* RESPONSIVE */
        @media (max-width: 1024px) {{
            .grid-4 {{ grid-template-columns: repeat(2, 1fr); }}
            .efectores-grid {{ grid-template-columns: repeat(2, 1fr); }}
            .navbar {{ padding: 14px 24px; }}
            .hero, .tabs-nav, .main-container {{ padding: 20px 24px; }}
        }}
        @media (max-width: 768px) {{
            .navbar {{ flex-direction: column; align-items: flex-start; gap: 14px; }}
            .nav-actions {{ width: 100%; }}
            .btn-naranja {{ width: 100%; justify-content: center; }}
            .grid-4, .grid-2, .efectores-grid, .programas-grid {{ grid-template-columns: 1fr; }}
            .hero h1 {{ font-size: 24px; }}
            #mapa-leaflet-container {{ height: 460px; }}
        }}
    </style>
</head>
<body>

    <!-- NAVBAR INSTITUCIONAL -->
    <header class="navbar">
        <div class="navbar-brand">
            <div class="logo-3f">
                {f'<img src="data:image/png;base64,{b64_logo}" alt="Logo 3F">' if b64_logo else '<img src="../logo.png" alt="Logo 3F">'}
            </div>
            <div class="brand-text">
                <strong>Municipalidad de Tres de Febrero</strong>
                <small>Secretaría de Educación y Desarrollo Humano • ASIS-Educación</small>
            </div>
        </div>
        <div class="nav-actions">
            <a href="../index.html" class="btn-naranja" style="background: var(--azul-primario); text-decoration: none; display: inline-flex; align-items: center; justify-content: center;">
                <span>🏥 Ver Tablero de Salud</span>
            </a>
            <button onclick="descargarWordEducacion()" class="btn-naranja">
                📥 Descargar Informe ASIS-Educación (.docx)
            </button>
        </div>
    </header>

    <!-- HERO SECTION -->
    <section class="hero">
        <h1>Análisis de Situación Educativa y Diagnóstico Distrital</h1>
        <p>
            Plataforma interactiva geo-estadística de los 457 radios censales del Partido de Tres de Febrero (06840). Integración integral de datos censales definitivos <strong>Censo 2022 (INDEC)</strong>, estudios de la <strong>Universidad Nacional de Tres de Febrero (UNTREF)</strong> y red de <strong>27 Jardines Municipales, EMAC, EMMU y CAPACYT</strong>.
        </p>
    </section>

    <!-- TABS DE NAVEGACIÓN -->
    <nav class="tabs-nav">
        <button class="tab-btn active" onclick="switchTab('resumen', this)">📊 Resumen Distrital e Indicadores (Censo 2022)</button>
        <button class="tab-btn" onclick="switchTab('mapa', this)">🗺️ Cartografía SIG y Red de Establecimientos</button>
        <button class="tab-btn" onclick="switchTab('graficos', this)">📈 Suite de Gráficos Analíticos y TIC</button>
        <button class="tab-btn" onclick="switchTab('directorio', this)">🏫 Directorio: 27 Jardines, EMAC, EMMU y CAPACYT</button>
        <button class="tab-btn" onclick="switchTab('programas', this)">✨ Programas de Apoyo, FinEs y Alfabetización</button>
    </nav>

    <!-- MAIN CONTENT -->
    <main class="main-container">

        <!-- PESTAÑA 1: RESUMEN DISTRITAL -->
        <div id="tab-resumen" class="tab-pane active">
            <div class="grid-4">
                <div class="kpi-card">
                    <div class="kpi-title">Población Total Censada</div>
                    <div class="kpi-val">364.176</div>
                    <div class="kpi-sub">52,5% Mujeres • 47,5% Varones (Censo 2022)</div>
                </div>
                <div class="kpi-card orange">
                    <div class="kpi-title">Asistencia Escolar Primaria (6-11)</div>
                    <div class="kpi-val">99,1%</div>
                    <div class="kpi-sub">Cobertura universal obligatoria en 3F</div>
                </div>
                <div class="kpi-card green">
                    <div class="kpi-title">Graduados Univ. / Posgrado (≥25)</div>
                    <div class="kpi-val">16,8%</div>
                    <div class="kpi-sub">vs. 10,4% Promedio 24 Partidos del GBA</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-title">Red Primera Infancia Municipal</div>
                    <div class="kpi-val">27 Jardines</div>
                    <div class="kpi-sub">Con Jornada Completa, Almuerzo e Inglés</div>
                </div>
            </div>

            <div class="grid-2">
                <div class="card-panel">
                    <h2>📊 Condición de Asistencia por Edad en Tres de Febrero</h2>
                    <p class="desc">Distribución porcentual de la población censada en viviendas particulares según condición de asistencia escolar en establecimientos formales (INDEC 2022):</p>
                    <canvas id="chartAsistenciaEdad" height="230"></canvas>
                </div>
                <div class="card-panel">
                    <h2>🎓 Máximo Nivel Educativo Alcanzado: 3F vs GBA</h2>
                    <p class="desc">Comparativa del nivel educativo completado en la población adulta de 25 años y más, evidenciando el liderazgo académico distrital impulsado por UNTREF y CAPACYT:</p>
                    <canvas id="chartNivelAlcanzado" height="230"></canvas>
                </div>
            </div>

            <div class="card-panel">
                <h2>🌐 Impacto Socioterritorial Universitario: UNTREF y Observatorio del Conurbano</h2>
                <p class="desc">
                    El Partido de Tres de Febrero presenta un comportamiento educativo diferenciado en la Región Metropolitana. Según las encuestas y datos sistematizados por la <strong>Universidad Nacional de Tres de Febrero (UNTREF)</strong> y el <strong>Observatorio del Conurbano Bonaerense (UNGS/OIDBA)</strong>, el acceso de jóvenes de 18 a 24 años a la educación superior en 3F alcanza el <strong>48,6%</strong>, superando en más de 8 puntos porcentuales la media provincial. Este fenómeno se fundamenta en la integración de las sedes universitarias en Caseros y Sáenz Peña con la red de escuelas medias locales y la oferta técnica municipal.
                </p>
            </div>
        </div>

        <!-- PESTAÑA 2: CARTOGRAFÍA SIG -->
        <div id="tab-mapa" class="tab-pane">
            <div class="card-panel">
                <div class="map-controls">
                    <div>
                        <h2 style="margin-bottom: 4px;">🗺️ Cartografía SIG de Infraestructura Educativa Municipal</h2>
                        <p class="desc" style="margin-bottom: 0;">Superposición de las 15 localidades (457 radios censales del INDEC `06840`) e íconos georreferenciados de Jardines, EMAC, EMMU y UNTREF.</p>
                    </div>
                    <div>
                        <!-- Botón para Pantalla Completa (funciona idéntico a Salud) -->
                        <button onclick="abrirMapaPantallaCompleta()" class="btn-secundario" style="background: var(--naranja); color: #fff; border: none;">
                            🖥️ Ampliar Mapa para Pantalla Completa
                        </button>
                    </div>
                </div>
                <div id="mapa-leaflet-container"></div>
            </div>
        </div>

        <!-- PESTAÑA 3: SUITE DE GRÁFICOS Y TIC -->
        <div id="tab-graficos" class="tab-pane">
            <div class="card-panel">
                <h2>📈 Suite Analítica de Educación, Conectividad y Determinantes TIC</h2>
                <p class="desc">Gráficos renderizados en alta resolución a partir del procesamiento estadístico de microdatos definitivos del Censo 2022 (INDEC) y relevamientos municipales:</p>
            </div>

            <div class="grid-2">
                <div class="card-panel" style="text-align: center;">
                    <h3 style="color: var(--azul-primario); margin-bottom: 12px; font-size: 16px;">Acceso a TIC y Brecha Digital en Hogares de 3F vs GBA</h3>
                    {f'<img src="data:image/png;base64,{b64_imgs.get("grafico_brecha_digital_tic_3f.png", "")}" alt="Brecha Digital TIC" style="max-width: 100%; height: auto; border-radius: 8px;">' if b64_imgs.get("grafico_brecha_digital_tic_3f.png") else '<p>Gráfico no disponible</p>'}
                    <p style="font-size: 12px; color: var(--neutro-700); margin-top: 10px;">El 94,5% de los hogares de 3F cuenta con celular con internet y 86,8% con internet fija.</p>
                </div>
                <div class="card-panel" style="text-align: center;">
                    <h3 style="color: var(--azul-primario); margin-bottom: 12px; font-size: 16px;">Distribución de los 27 Jardines Municipales por Corredor</h3>
                    {f'<img src="data:image/png;base64,{b64_imgs.get("grafico_distribucion_jardines_localidades.png", "")}" alt="Jardines por Corredor" style="max-width: 100%; height: auto; border-radius: 8px;">' if b64_imgs.get("grafico_distribucion_jardines_localidades.png") else '<p>Gráfico no disponible</p>'}
                    <p style="font-size: 12px; color: var(--neutro-700); margin-top: 10px;">Despliegue territorial de la Primera Infancia, con 10 jardines en Jornada Completa con Almuerzo.</p>
                </div>
            </div>

            <div class="grid-2">
                <div class="card-panel" style="text-align: center;">
                    <h3 style="color: var(--azul-primario); margin-bottom: 12px; font-size: 16px;">Condición de Asistencia Escolar según Edad (Censo 2022)</h3>
                    {f'<img src="data:image/png;base64,{b64_imgs.get("grafico_asistencia_por_edad_3f.png", "")}" alt="Asistencia por Edad" style="max-width: 100%; height: auto; border-radius: 8px;">' if b64_imgs.get("grafico_asistencia_por_edad_3f.png") else '<p>Gráfico no disponible</p>'}
                </div>
                <div class="card-panel" style="text-align: center;">
                    <h3 style="color: var(--azul-primario); margin-bottom: 12px; font-size: 16px;">Comparativa del Máximo Nivel Educativo Alcanzado (3F vs GBA)</h3>
                    {f'<img src="data:image/png;base64,{b64_imgs.get("grafico_nivel_educativo_3f_vs_gba.png", "")}" alt="Nivel Educativo" style="max-width: 100%; height: auto; border-radius: 8px;">' if b64_imgs.get("grafico_nivel_educativo_3f_vs_gba.png") else '<p>Gráfico no disponible</p>'}
                </div>
            </div>
        </div>

        <!-- PESTAÑA 4: DIRECTORIO DE ESTABLECIMIENTOS -->
        <div id="tab-directorio" class="tab-pane">
            <div class="card-panel">
                <h2>🏫 Directorio de Oferta Formativa y Red de 27 Jardines Municipales</h2>
                <p class="desc">Listado oficial de instituciones gestionadas por la Secretaría de Educación y Desarrollo Humano de Tres de Febrero:</p>
                
                <h3 style="color: var(--azul-primario); font-size: 18px; margin: 24px 0 16px 0; border-bottom: 2px solid var(--naranja); padding-bottom: 8px;">🎨 Escuelas Superiores de Arte, Música y Formación Docente</h3>
                <div class="efectores-grid">
                    <div class="efector-card">
                        <div>
                            <span class="efector-tag orange">Arte y Comunicación</span>
                            <h3>EMAC — Escuela Municipal de Arte y Comunicación</h3>
                            <p>Institución pública gratuita referente con tramos profesionales en: Artes Visuales, Arte Dramático, Teatro, Danzas Clásicas y Contemporáneas, Diseño y Confección de Indumentaria, y Periodismo Digital / Escritura Creativa.</p>
                        </div>
                        <div class="efector-footer">📍 Urquiza 4750, Caseros • Presencial y Gratuita</div>
                    </div>
                    <div class="efector-card">
                        <div>
                            <span class="efector-tag">Formación Musical</span>
                            <h3>EMMU — Escuela Municipal de Música</h3>
                            <p>Formación instrumental integral y técnica en piano, violín, saxo, guitarra y canto lírico. Muestras artísticas abiertas a la comunidad y vinculación con la EMAC.</p>
                        </div>
                        <div class="efector-footer">📍 Caseros Centro • Todos los niveles</div>
                    </div>
                    <div class="efector-card">
                        <div>
                            <span class="efector-tag green">Formación Superior Docente</span>
                            <h3>CAPACYT — Centro Municipal de Capacitación Superior</h3>
                            <p>Profesorados oficiales con título de validez nacional en Educación Inicial, Educación Primaria y Psicología. Diplomaturas en Ciencia y Tecnología.</p>
                        </div>
                        <div class="efector-footer">📍 Sede Central Tres de Febrero • Título Oficial</div>
                    </div>
                </div>

                <h3 style="color: var(--azul-primario); font-size: 18px; margin: 34px 0 16px 0; border-bottom: 2px solid var(--naranja); padding-bottom: 8px;">🧸 Red de 27 Jardines de Infantes y Maternales Municipales (Dirección de Primera Infancia)</h3>
                <div class="efectores-grid">
                    <div class="efector-card">
                        <div>
                            <span class="efector-tag orange">Jornada Completa c/ Almuerzo</span>
                            <h3>Jardín Municipal "Ardillitas Traviesas"</h3>
                            <p>Salas de 3, 4 y 5 años. Modalidad de Jornada Completa con servicio alimentario. Estimulación temprana, iniciación al inglés y robótica.</p>
                        </div>
                        <div class="efector-footer">📍 Caseros / Santos Lugares</div>
                    </div>
                    <div class="efector-card">
                        <div>
                            <span class="efector-tag orange">Jornada Completa c/ Almuerzo</span>
                            <h3>Jardín Municipal "Arenales"</h3>
                            <p>Educación inicial integral. Talleres de psicomotricidad, expresión artística y alfabetización digital adaptada a primera infancia.</p>
                        </div>
                        <div class="efector-footer">📍 Ciudadela Sur</div>
                    </div>
                    <div class="efector-card">
                        <div>
                            <span class="efector-tag orange">Jornada Completa c/ Almuerzo</span>
                            <h3>Jardín Municipal "Evita"</h3>
                            <p>Sede histórica de primera infancia. Incorporación de jornada completa y talleres de participación con familias y comunidad escolar.</p>
                        </div>
                        <div class="efector-footer">📍 Loma Hermosa / Podestá</div>
                    </div>
                    <div class="efector-card">
                        <div>
                            <span class="efector-tag">Jornada Simple</span>
                            <h3>Jardín Municipal "José Hernández"</h3>
                            <p>Salas turno mañana y turno tarde. Articulación pedagógica directa con escuelas primarias provinciales del corredor centro.</p>
                        </div>
                        <div class="efector-footer">📍 Sáenz Peña</div>
                    </div>
                    <div class="efector-card">
                        <div>
                            <span class="efector-tag orange">Jornada Completa c/ Almuerzo</span>
                            <h3>Jardín Municipal "Ternuritas"</h3>
                            <p>Atención integral maternal e inicial. Nutrición escolar profesionalizada y desarrollo de habilidades científicas tempranas.</p>
                        </div>
                        <div class="efector-footer">📍 Villa Bosch / Martín Coronado</div>
                    </div>
                    <div class="efector-card">
                        <div>
                            <span class="efector-tag">Red Distrital Ampliada</span>
                            <h3>22 Jardines Municipales Restantes</h3>
                            <p>El municipio opera un total de 27 jardines cubriendo el 100% de las localidades (Churruca, El Libertador, 11 de Septiembre, Ciudad Jardín, Raffo, etc.), garantizando vacantes en sala de 4 y 5 años.</p>
                        </div>
                        <div class="efector-footer">📍 15 Localidades del Partido (`06840`)</div>
                    </div>
                </div>
            </div>
        </div>

        <!-- PESTAÑA 5: PROGRAMAS MUNICIPALES -->
        <div id="tab-programas" class="tab-pane">
            <div class="card-panel">
                <h2>✨ Programas Municipales y Políticas de Acompañamiento Educativo</h2>
                <p class="desc">Iniciativas de la Secretaría de Educación destinadas a garantizar la terminalidad, inclusión digital y apoyo psicopedagógico:</p>
                
                <div class="programas-grid">
                    <div class="prog-badge">
                        <h4>🎯 Plan FinEs Municipal — Terminalidad Secundaria</h4>
                        <p>Orientado a jóvenes y adultos de ≥18 años que asistieron en el pasado y no finalizaron sus estudios (población que el Censo 2022 ubicó en 50,2% para 18-24 años y 76,4% para 25-29 años). Cursada descentralizada en sedes comunitarias.</p>
                    </div>
                    <div class="prog-badge">
                        <h4>📚 Programas de Apoyo Escolar y Alfabetización</h4>
                        <p>Centros municipales de tutoría y apoyo escolar para nivel primario y secundario en todos los CAPS y sedes comunitarias, enfocados en reducir la repitencia y fortalecer lectocomprensión y matemáticas.</p>
                    </div>
                    <div class="prog-badge">
                        <h4>🤖 Robótica, Pensamiento Científico e Inglés en Jardines</h4>
                        <p>Introducción del idioma inglés y kits de robótica educativa tempranos en los 27 Jardines Municipales para cerrar la brecha digital desde los primeros años de escolarización.</p>
                    </div>
                    <div class="prog-badge">
                        <h4>🎓 Articulación UNTREF — Becas y Orientación Vocacional</h4>
                        <p>Programa municipal de ferias universitarias, test de orientación vocacional y vinculación directa para que los egresados secundarios de 3F continúen carreras de grado en la Universidad Nacional de Tres de Febrero.</p>
                    </div>
                </div>
            </div>
        </div>

    </main>

    <!-- FOOTER -->
    <footer>
        <div class="footer-content">
            <div>
                <p class="inst">MUNICIPALIDAD DE TRES DE FEBRERO • SECRETARÍA DE EDUCACIÓN Y DESARROLLO HUMANO</p>
                <p class="sub">Partido 06840 — Región Metropolitana de Buenos Aires • Análisis de Situación Educativa (ASIS-Educación 2026)</p>
            </div>
            <div>
                <p class="sub" style="text-align: right;">Desarrollado con datos definitivos Censo 2022 INDEC, UNTREF y cartografía IGN.</p>
            </div>
        </div>
    </footer>

    <!-- MODAL MAPA PANTALLA COMPLETA -->
    <div id="mapa-modal-container">
        <div class="modal-header">
            <h3>🗺️ Cartografía SIG — Sistema Educativo de Tres de Febrero (Pantalla Completa)</h3>
            <button class="btn-close-modal" onclick="cerrarMapaPantallaCompleta()">❌ Cerrar Pantalla Completa</button>
        </div>
        <div id="mapa-fullscreen-leaflet"></div>
    </div>

    <!-- SCRIPTS JS INTERACTIVOS -->
    <script>
        // 1. GESTIÓN DE TABS
        function switchTab(tabId, btnElement) {{
            document.querySelectorAll('.tab-pane').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
            
            const targetPane = document.getElementById('tab-' + tabId);
            if (targetPane) targetPane.classList.add('active');
            if (btnElement) btnElement.classList.add('active');
            
            if (tabId === 'mapa' && window.mapaLeaflet) {{
                setTimeout(() => {{ window.mapaLeaflet.invalidateSize(); }}, 200);
            }}
        }}

        // 2. DESCARGA DEL ARCHIVO WORD (.DOCX) EN BLOB
        function descargarWordEducacion() {{
            const b64Data = "{b64_docx}";
            if (!b64Data || b64Data.length < 100) {{
                alert("El archivo Word no está disponible para descarga en este momento.");
                return;
            }}
            try {{
                const byteCharacters = atob(b64Data);
                const byteNumbers = new Array(byteCharacters.length);
                for (let i = 0; i < byteCharacters.length; i++) {{
                    byteNumbers[i] = byteCharacters.charCodeAt(i);
                }}
                const byteArray = new Uint8Array(byteNumbers);
                const blob = new Blob([byteArray], {{ type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document" }});
                
                const link = document.createElement("a");
                link.href = URL.createObjectURL(blob);
                link.download = "informe_situacion_educativa_3f.docx";
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
            }} catch(e) {{
                alert("Hubo un problema procesando la descarga en tu dispositivo.");
            }}
        }}

        // 3. INICIALIZACIÓN DE GRÁFICOS CHART.JS (TAB 1)
        window.addEventListener('DOMContentLoaded', () => {{
            // Gráfico 1: Asistencia
            const ctxAsist = document.getElementById('chartAsistenciaEdad');
            if (ctxAsist) {{
                new Chart(ctxAsist, {{
                    type: 'bar',
                    data: {{
                        labels: ['3-5 años', '6-11 años', '12-17 años', '18-24 años', '25-29 años', '30+ años'],
                        datasets: [
                            {{ label: 'Asiste Actualmente (%)', data: [68.2, 99.1, 95.4, 48.6, 22.4, 4.8], backgroundColor: '#163C68' }},
                            {{ label: 'Asistió en el Pasado (%)', data: [0.8, 0.2, 4.1, 50.2, 76.4, 93.7], backgroundColor: '#3B93F7' }},
                            {{ label: 'Nunca Asistió (%)', data: [31.0, 0.7, 0.5, 1.2, 1.2, 1.5], backgroundColor: '#F69321' }}
                        ]
                    }},
                    options: {{
                        responsive: true,
                        scales: {{ y: {{ beginAtZero: true, max: 110 }} }},
                        plugins: {{ legend: {{ position: 'top' }} }}
                    }}
                }});
            }}

            // Gráfico 2: Nivel Alcanzado
            const ctxNiv = document.getElementById('chartNivelAlcanzado');
            if (ctxNiv) {{
                new Chart(ctxNiv, {{
                    type: 'bar',
                    data: {{
                        labels: ['Univ. Completo', 'Univ. Incompleto', 'Terciario Comp.', 'Secundario Comp.', 'Secundario Incomp.', 'Primario Comp.'],
                        datasets: [
                            {{ label: 'Tres de Febrero (%)', data: [16.8, 14.2, 8.5, 27.6, 16.4, 13.2], backgroundColor: '#163C68' }},
                            {{ label: 'Promedio GBA (%)', data: [10.4, 11.8, 6.2, 24.1, 24.8, 18.6], backgroundColor: '#F69321' }}
                        ]
                    }},
                    options: {{
                        indexAxis: 'y',
                        responsive: true,
                        scales: {{ x: {{ beginAtZero: true, max: 35 }} }},
                        plugins: {{ legend: {{ position: 'bottom' }} }}
                    }}
                }});
            }}

            // Inicializar Mapa Leaflet Normal
            inicializarMapaEducacion('mapa-leaflet-container', false);
        }});

        // 4. INICIALIZACIÓN MAPA LEAFLET SIG (CON CARTOGRAFÍA REAL DEL PARTIDO Y MARCADORES)
        const geojsonData = {geojson_json_str};

        const establecimientos = [
            {{ nom: "EMAC — Escuela Municipal de Arte y Comunicación", lat: -34.6065, lng: -58.5641, desc: "Urquiza 4750, Caseros. Artes Visuales, Teatro, Danza, Diseño, Periodismo.", icon: "🎨", color: "#F69321" }},
            {{ nom: "EMMU — Escuela Municipal de Música & CAPACYT", lat: -34.6052, lng: -58.5630, desc: "Caseros Centro. Instrumentos, Canto y Profesorados Inicial/Primaria.", icon: "🎵", color: "#163C68" }},
            {{ nom: "UNTREF — Sede Central Caseros", lat: -34.6058, lng: -58.5620, desc: "Valentín Gómez 4752, Caseros. Universidad Nacional de Tres de Febrero.", icon: "🎓", color: "#3B93F7" }},
            {{ nom: "UNTREF — Sede Sáenz Peña", lat: -34.5940, lng: -58.5280, desc: "Mosconi 2736, Sáenz Peña. Carreras de ingeniería, arte y tecnología.", icon: "🎓", color: "#3B93F7" }},
            {{ nom: "Jardín Municipal 'Ardillitas Traviesas'", lat: -34.6040, lng: -58.5580, desc: "Caseros. Jornada Completa con Almuerzo e Inglés.", icon: "🧸", color: "#13B423" }},
            {{ nom: "Jardín Municipal 'Arenales'", lat: -34.6320, lng: -58.5380, desc: "Ciudadela Sur. Primera Infancia e Iniciación Digital.", icon: "🧸", color: "#13B423" }},
            {{ nom: "Jardín Municipal 'Evita'", lat: -34.5680, lng: -58.5890, desc: "Loma Hermosa / Podestá. Jornada Completa.", icon: "🧸", color: "#13B423" }},
            {{ nom: "Jardín Municipal 'José Hernández'", lat: -34.5910, lng: -58.5340, desc: "Sáenz Peña. Salas turno mañana y tarde.", icon: "🧸", color: "#13B423" }},
            {{ nom: "Jardín Municipal 'Ternuritas'", lat: -34.5820, lng: -58.5780, desc: "Villa Bosch. Primera Infancia y Robótica temprana.", icon: "🧸", color: "#13B423" }}
        ];

        function inicializarMapaEducacion(contenedorId, esFullscreen) {{
            const elem = document.getElementById(contenedorId);
            if (!elem) return;
            
            const map = L.map(contenedorId).setView([-34.598, -58.565], 13);
            L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
                attribution: '© OpenStreetMap • cartografía oficial IGN / INDEC Tres de Febrero (`06840`)'
            }}).addTo(map);

            if (geojsonData && geojsonData.features && geojsonData.features.length > 0) {{
                L.geoJSON(geojsonData, {{
                    style: function(feature) {{
                        return {{
                            color: '#163C68',
                            weight: 1.8,
                            fillColor: '#B8D0EB',
                            fillOpacity: 0.35
                        }};
                    }},
                    onEachFeature: function(feature, layer) {{
                        const cod = feature.properties.TOPONYM || feature.properties.LINK || "Radio 3F";
                        layer.bindPopup(`<strong>📍 Partido 06840 - Tres de Febrero</strong><br>Polígono oficial INDEC: ${{cod}}`);
                    }}
                }}).addTo(map);
            }}

            establecimientos.forEach(est => {{
                const customIcon = L.divIcon({{
                    className: 'custom-leaflet-icon',
                    html: `<div style="background: ${{est.color}}; color: white; width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 16px; box-shadow: 0 2px 6px rgba(0,0,0,0.4); border: 2px solid white;">${{est.icon}}</div>`,
                    iconSize: [32, 32],
                    iconAnchor: [16, 16]
                }});
                
                L.marker([est.lat, est.lng], {{ icon: customIcon }}).addTo(map)
                 .bindPopup(`<div style="min-width: 200px;">
                    <strong style="color: var(--azul-primario); font-size: 14px;">${{est.icon}} ${{est.nom}}</strong>
                    <p style="font-size: 12px; margin: 6px 0 0 0; color: #333;">${{est.desc}}</p>
                 </div>`);
            }});

            if (!esFullscreen) window.mapaLeaflet = map;
            else window.mapaFullscreenLeaflet = map;
        }}

        // 5. MODAL MAPA PANTALLA COMPLETA
        function abrirMapaPantallaCompleta() {{
            const modal = document.getElementById('mapa-modal-container');
            if (modal) {{
                modal.classList.add('active');
                setTimeout(() => {{
                    if (!window.mapaFullscreenLeaflet) {{
                        inicializarMapaEducacion('mapa-fullscreen-leaflet', true);
                    }} else {{
                        window.mapaFullscreenLeaflet.invalidateSize();
                    }}
                }}, 250);
            }}
        }}

        function cerrarMapaPantallaCompleta() {{
            const modal = document.getElementById('mapa-modal-container');
            if (modal) modal.classList.remove('active');
        }}
    </script>
</body>
</html>"""

    with open(html_out, 'w', encoding='utf-8') as f:
        f.write(html_content)
        
    print(f"\n[ÉXITO TABLERO HTML DE EDUCACIÓN GENERADO EN]: {html_out}")
    print(f" -> Tamaño del tablero autónomo: {os.path.getsize(html_out)} bytes ({os.path.getsize(html_out)/1024:.1f} KB)")

if __name__ == "__main__":
    generar_tablero_educacion()
