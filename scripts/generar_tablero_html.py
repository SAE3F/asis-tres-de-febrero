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

def generar_tablero_self_contained():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    salidas_dir = os.path.join(base_dir, 'salidas')
    datos_dir = os.path.join(base_dir, 'datos')
    
    html_root = os.path.join(base_dir, 'visualizador_asis_tres_de_febrero.html')
    html_salidas = os.path.join(salidas_dir, 'visualizador_asis_tres_de_febrero.html')
    
    print("--- GENERANDO TABLERO HTML CON ICONOS OFICIALES, PANTALLA COMPLETA MÓVIL Y DESCARGA WORD BLOB ---")
    
    # 1. Cargar GeoJSON exacto de los 457 polígonos sin huecos para incrustarlo como objeto JS
    geojson_path = os.path.join(datos_dir, 'radios_censales_3f.geojson')
    if os.path.exists(geojson_path):
        with open(geojson_path, 'r', encoding='utf-8') as gf:
            geojson_data = json.load(gf)
    else:
        geojson_data = {"type": "FeatureCollection", "features": []}
    geojson_json_str = json.dumps(geojson_data, ensure_ascii=False)
    
    # 2. Convertir el Logo Municipal (logo.png) a Base64
    logo_path = os.path.join(base_dir, 'logo.png')
    if not os.path.exists(logo_path):
        logo_path = os.path.join(salidas_dir, 'logo.png')
    b64_logo = get_base64_file(logo_path)
    print(f" -> Logo municipal convertido a Base64 (longitud: {len(b64_logo)} caracteres)")

    # 3. Convertir el archivo Word COMPLETO más reciente a Base64 para que la descarga sea 100% infalible vía Blob en móviles y PC
    docx_candidatos = [
        os.path.join(base_dir, 'informe_situacion_salud_tres_de_febrero_COMPLETO.docx'),
        os.path.join(base_dir, 'informe_situacion_salud_tres_de_febrero_ACTUALIZADO.docx'),
        os.path.join(salidas_dir, 'informe_situacion_salud_tres_de_febrero_COMPLETO.docx'),
        os.path.join(base_dir, 'informe_situacion_salud_tres_de_febrero.docx')
    ]
    docx_validos = [f for f in docx_candidatos if os.path.exists(f)]
    docx_path = max(docx_validos, key=os.path.getmtime) if docx_validos else docx_candidatos[0]
    print(f" -> Incrustando documento Word más reciente: {os.path.basename(docx_path)}")
    b64_docx = get_base64_file(docx_path)
    print(f" -> Archivo Word convertido a Base64 para descarga directa en móvil/PC (longitud: {len(b64_docx)} caracteres)")

    # 4. Convertir las 4 imágenes PNG de la suite a Base64
    img_names = [
        'grafico_dependencia_por_localidad_3f.png',
        'grafico_piramide_demografica_3f.png',
        'grafico_cobertura_vs_infraestructura_3f.png',
        'grafico_capacidad_efectores_3f.png'
    ]
    b64_imgs = {}
    for nom in img_names:
        path_sal = os.path.join(salidas_dir, nom)
        path_root = os.path.join(base_dir, nom)
        if os.path.exists(path_sal):
            b64_imgs[nom] = get_base64_file(path_sal)
        elif os.path.exists(path_root):
            b64_imgs[nom] = get_base64_file(path_root)
        else:
            b64_imgs[nom] = ""
            
    print(f" -> Imágenes convertidas a Base64 incrustadas: {sum(1 for v in b64_imgs.values() if v)}")
    print(f" -> Polígonos de cartografía real incrustados en JS: {len(geojson_data.get('features', []))}")

    html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0, user-scalable=yes">
    <title>Salud — Municipalidad de Tres de Febrero (Análisis de Situación ASIS)</title>
    <!-- Google Fonts idénticas a Educación Web: Montserrat & Inter -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <!-- Chart.js -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <!-- Leaflet para cartografía poligonal integrada -->
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <style>
        :root {{
            /* Paleta Oficial Municipalidad de Tres de Febrero (Copiada de Educación Web) */
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

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Montserrat', sans-serif;
            color: var(--neutro-900);
            background: var(--neutro-0);
            -webkit-font-smoothing: antialiased;
            overflow-x: hidden;
            display: flex;
            flex-direction: column;
            min-height: 100vh;
        }}

        /* ============ TOP NAV BAR INSTITUCIONAL ============ */
        .topbar {{
            background: var(--azul-primario);
            height: 5px;
            width: 100%;
        }}

        .navbar {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 16px 48px;
            background: #fff;
            border-bottom: 1px solid var(--neutro-300);
            position: sticky;
            top: 0;
            z-index: 100;
            box-shadow: var(--shadow-sm);
            flex-wrap: wrap;
            gap: 16px;
        }}

        .navbar-brand {{
            display: flex;
            align-items: center;
            gap: 16px;
            max-width: 100%;
        }}

        .logo-3f {{
            width: 52px;
            height: 52px;
            border-radius: var(--radius-sm);
            overflow: hidden;
            flex-shrink: 0;
            display: flex;
            align-items: center;
            justify-content: center;
        }}

        .logo-3f img {{
            max-width: 100%;
            max-height: 100%;
            object-fit: contain;
            display: block;
        }}

        .brand-text {{
            display: flex;
            flex-direction: column;
        }}

        .brand-text strong {{
            font-size: 16px;
            font-weight: 800;
            color: var(--azul-primario);
            line-height: 1.2;
            letter-spacing: -0.3px;
        }}

        .brand-text small {{
            font-size: 12px;
            font-weight: 600;
            color: var(--neutro-700);
            margin-top: 2px;
        }}

        .nav-actions {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}

        .btn-naranja {{
            background: var(--naranja);
            color: #fff;
            padding: 10px 18px;
            border-radius: var(--radius-sm);
            font-size: 13px;
            font-weight: 700;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            transition: background 0.2s, transform 0.1s;
            box-shadow: var(--shadow-sm);
            white-space: normal;
            text-align: center;
            cursor: pointer;
            border: none;
        }}

        .btn-naranja:hover {{
            background: var(--naranja-oscuro);
            transform: translateY(-1px);
        }}

        /* ============ BARRA DE PESTAÑAS (TABS) FORMALES ============ */
        .tabs-nav {{
            background: var(--neutro-100);
            border-bottom: 1px solid var(--neutro-300);
            padding: 0 48px;
            display: flex;
            overflow-x: auto;
            gap: 6px;
            -webkit-overflow-scrolling: touch;
            scrollbar-width: thin;
        }}

        .tab-btn {{
            font-family: 'Montserrat', sans-serif;
            font-size: 13px;
            font-weight: 600;
            color: var(--neutro-700);
            background: transparent;
            border: none;
            padding: 14px 18px;
            cursor: pointer;
            position: relative;
            white-space: nowrap;
            transition: color 0.2s, background 0.2s;
            flex-shrink: 0;
            -webkit-tap-highlight-color: transparent;
            touch-action: manipulation;
            user-select: none;
            -webkit-user-select: none;
        }}

        .tab-btn:hover {{
            color: var(--azul-primario);
            background: rgba(22, 60, 104, 0.04);
        }}

        .tab-btn.active {{
            color: var(--azul-primario);
            font-weight: 700;
        }}

        .tab-btn.active::after {{
            content: '';
            position: absolute;
            bottom: 0;
            left: 0;
            width: 100%;
            height: 4px;
            background: var(--naranja);
            border-radius: 4px 4px 0 0;
        }}

        /* ============ HERO SECTION ============ */
        .hero {{
            background: linear-gradient(135deg, var(--azul-oscuro) 0%, var(--azul-primario) 100%);
            color: #fff;
            padding: 40px 48px;
            border-radius: var(--radius-lg);
            box-shadow: var(--shadow-lg);
            margin-bottom: 32px;
            position: relative;
            overflow: hidden;
        }}

        .hero-badge {{
            display: inline-block;
            background: var(--naranja);
            color: #fff;
            font-size: 11px;
            font-weight: 700;
            padding: 5px 12px;
            border-radius: 20px;
            text-transform: uppercase;
            letter-spacing: 0.8px;
            margin-bottom: 14px;
        }}

        .hero h1 {{
            font-size: 30px;
            font-weight: 800;
            line-height: 1.25;
            margin-bottom: 12px;
        }}

        .hero p {{
            font-size: 15px;
            font-weight: 400;
            line-height: 1.6;
            color: var(--azul-claro);
            max-width: 850px;
        }}

        /* ============ LAYOUT PRINCIPAL & CARDS ============ */
        .main-container {{
            max-width: 1280px;
            width: 100%;
            margin: 0 auto;
            padding: 32px 48px;
            flex: 1;
        }}

        .grid-4 {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
            gap: 20px;
            margin-bottom: 32px;
        }}

        .kpi-card {{
            background: #fff;
            border: 1px solid var(--neutro-300);
            border-radius: var(--radius-md);
            padding: 24px;
            box-shadow: var(--shadow-sm);
            transition: transform 0.2s, box-shadow 0.2s;
            position: relative;
            border-top: 4px solid var(--azul-primario);
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }}

        .kpi-card:hover {{
            transform: translateY(-3px);
            box-shadow: var(--shadow-md);
        }}

        .kpi-card.naranja {{ border-top-color: var(--naranja); }}
        .kpi-card.verde {{ border-top-color: var(--verde); }}
        .kpi-card.info {{ border-top-color: var(--azul-info); }}

        .kpi-label {{
            font-size: 11px;
            font-weight: 700;
            color: var(--neutro-500);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        .kpi-val {{
            font-size: 32px;
            font-weight: 800;
            color: var(--azul-primario);
            margin: 8px 0 4px 0;
            line-height: 1;
        }}

        .kpi-val span {{ font-size: 14px; font-weight: 600; color: var(--neutro-700); }}
        .kpi-sub {{ font-size: 12px; font-weight: 600; color: var(--neutro-700); }}
        .kpi-detail {{ font-size: 11px; color: var(--neutro-500); margin-top: 4px; }}

        .card-panel {{
            background: #fff;
            border: 1px solid var(--neutro-300);
            border-radius: var(--radius-lg);
            padding: 28px;
            box-shadow: var(--shadow-md);
            margin-bottom: 28px;
            overflow: hidden;
            position: relative;
        }}

        .card-panel h2 {{
            font-size: 20px;
            font-weight: 700;
            color: var(--azul-primario);
            margin-bottom: 8px;
            display: flex;
            align-items: center;
            gap: 10px;
            flex-wrap: wrap;
        }}

        .card-panel p.desc {{
            font-size: 14px;
            color: var(--neutro-700);
            line-height: 1.6;
            margin-bottom: 16px;
        }}

        /* ============ REFERENCIAS Y FUENTES DE DATOS EN GRÁFICOS Y TABLAS ============ */
        .fuente-dato {{
            font-size: 11.5px;
            font-style: italic;
            color: var(--neutro-500);
            background: var(--neutro-100);
            border-left: 3px solid var(--azul-primario);
            padding: 8px 12px;
            margin-top: 14px;
            border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
            line-height: 1.4;
        }}

        .fuente-dato strong {{
            color: var(--neutro-700);
            font-style: normal;
        }}

        .grid-2 {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(420px, 1fr));
            gap: 24px;
            margin-bottom: 24px;
        }}

        #mapa-leaflet-container {{
            width: 100%;
            height: 680px;
            border-radius: var(--radius-md);
            border: 1px solid var(--neutro-300);
            z-index: 1;
            transition: all 0.25s ease;
        }}

        /* ============ MODO PANTALLA COMPLETA (FULLSCREEN) PARA EL MAPA ============ */
        #mapa-leaflet-container.fullscreen-active {{
            position: fixed !important;
            top: 0 !important;
            left: 0 !important;
            width: 100vw !important;
            height: 100vh !important;
            z-index: 999999 !important;
            border-radius: 0 !important;
            border: none !important;
            margin: 0 !important;
        }}

        .btn-fullscreen-close {{
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 1000000;
            background: var(--rojo);
            color: #fff;
            font-family: 'Montserrat', sans-serif;
            font-weight: 700;
            font-size: 13px;
            padding: 12px 20px;
            border-radius: 30px;
            border: 2px solid #fff;
            box-shadow: var(--shadow-xl);
            cursor: pointer;
            display: none;
            align-items: center;
            gap: 8px;
        }}

        /* ESTILOS PARA ICONOS Y LOGOS CIRCULARES EN EL MAPA LEAFLET */
        .icon-efector-div {{
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 50%;
            border: 2.5px solid #fff;
            box-shadow: 0 3px 10px rgba(0, 13, 29, 0.35);
            font-size: 16px;
            line-height: 1;
            cursor: pointer;
            transition: transform 0.2s;
        }}

        .icon-efector-div:hover {{
            transform: scale(1.15);
            z-index: 1000 !important;
        }}

        .programas-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
            gap: 12px;
            margin-top: 16px;
        }}

        .prog-badge {{
            background: var(--azul-claro);
            color: var(--azul-primario);
            border: 1px solid var(--azul-suave);
            border-radius: var(--radius-md);
            padding: 12px 14px;
            font-size: 12px;
            font-weight: 700;
            text-align: center;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            box-shadow: var(--shadow-sm);
        }}

        .prog-badge.highlight {{
            background: var(--naranja-claro);
            color: var(--naranja-oscuro);
            border-color: var(--naranja-suave);
        }}

        .efectores-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}

        .efector-card {{
            background: var(--neutro-0);
            border: 1px solid var(--neutro-300);
            border-radius: var(--radius-md);
            padding: 20px;
            border-left: 5px solid var(--azul-primario);
            box-shadow: var(--shadow-sm);
            display: flex;
            flex-direction: column;
        }}

        .efector-card.naranja {{ border-left-color: var(--naranja); }}
        .efector-card.rojo {{ border-left-color: var(--rojo); }}

        .efector-tag {{
            display: inline-block;
            align-self: flex-start;
            font-size: 10px;
            font-weight: 700;
            text-transform: uppercase;
            padding: 3px 8px;
            border-radius: 4px;
            background: var(--azul-claro);
            color: var(--azul-primario);
            margin-bottom: 8px;
        }}

        .efector-tag.rojo {{ background: #FFE5E5; color: var(--rojo); }}
        .efector-tag.naranja {{ background: var(--naranja-claro); color: var(--naranja-oscuro); }}

        .efector-card h4 {{ font-size: 16px; font-weight: 700; color: var(--neutro-900); margin-bottom: 4px; }}
        .efector-card p.loc {{ font-size: 12px; font-weight: 600; color: var(--neutro-500); margin-bottom: 8px; }}
        .efector-card p.txt {{ font-size: 13px; color: var(--neutro-700); line-height: 1.5; }}

        /* ============ FOOTER MUNICIPAL FORMAL ============ */
        footer {{
            background: var(--azul-oscuro);
            color: #fff;
            padding: 32px 48px;
            margin-top: auto;
            border-top: 4px solid var(--naranja);
        }}

        .footer-content {{
            max-width: 1280px;
            margin: 0 auto;
            display: flex;
            flex-direction: column;
            align-items: center;
            text-align: center;
            gap: 12px;
        }}

        .footer-content p.inst {{ font-size: 15px; font-weight: 700; color: #fff; }}
        .footer-content p.sub {{ font-size: 12px; color: var(--azul-suave); }}

        .hidden {{ display: none !important; }}

        /* ============ ADAPTACIÓN MÓVIL TOTAL (RESPONSIVE MOBILE-FIRST) ============ */
        @media (max-width: 1024px) {{
            .main-container {{ padding: 24px 24px; }}
            .navbar {{ padding: 14px 24px; }}
            .tabs-nav {{ padding: 0 24px; }}
            .hero {{ padding: 32px 28px; }}
        }}

        @media (max-width: 768px) {{
            .navbar {{
                flex-direction: column;
                align-items: flex-start;
                padding: 14px 16px;
                gap: 12px;
            }}
            .navbar-brand {{ width: 100%; }}
            .nav-actions {{ width: 100%; }}
            .btn-naranja {{ width: 100%; padding: 12px; font-size: 13px; }}
            
            .tabs-nav {{ padding: 0 12px; }}
            .tab-btn {{ padding: 12px 14px; font-size: 12px; }}
            
            .main-container {{ padding: 20px 14px; }}
            .hero {{ padding: 24px 18px; margin-bottom: 24px; }}
            .hero h1 {{ font-size: 24px; }}
            .hero p {{ font-size: 13px; }}
            
            .grid-4 {{ grid-template-columns: 1fr; gap: 14px; }}
            .grid-2 {{ grid-template-columns: 1fr; gap: 16px; }}
            
            .card-panel {{ padding: 20px 16px; margin-bottom: 20px; }}
            .card-panel h2 {{ font-size: 17px; }}
            .card-panel p.desc {{ font-size: 13px; margin-bottom: 16px; }}
            
            #mapa-leaflet-container {{ height: 480px; }}
            
            .efectores-grid {{ grid-template-columns: 1fr; gap: 14px; }}
            .programas-grid {{ grid-template-columns: 1fr 1fr; gap: 10px; }}
            
            footer {{ padding: 24px 16px; }}
            .footer-content p.inst {{ font-size: 13px; }}
            .footer-content p.sub {{ font-size: 11px; }}
        }}

        @media (max-width: 480px) {{
            .brand-text strong {{ font-size: 14px; }}
            .brand-text small {{ font-size: 11px; }}
            .logo-3f {{ width: 44px; height: 44px; }}
            
            .hero h1 {{ font-size: 20px; }}
            .kpi-val {{ font-size: 26px; }}
            .kpi-card {{ padding: 18px; }}
            
            #mapa-leaflet-container {{ height: 430px; }}
            .programas-grid {{ grid-template-columns: 1fr; }}
            .prog-badge {{ padding: 10px 12px; font-size: 12px; }}
        }}
    </style>
</head>
<body>

    <!-- BOTÓN FLOTANTE PARA CERRAR PANTALLA COMPLETA DEL MAPA -->
    <button id="btn-close-fullscreen" class="btn-fullscreen-close" onclick="toggleMapFullscreen(false)">
        ✖ Cerrar Pantalla Completa
    </button>

    <!-- TOP BAR MUNICIPAL -->
    <div class="topbar"></div>

    <!-- NAVBAR INSTITUCIONAL CON LOGO 3F -->
    <nav class="navbar">
        <div class="navbar-brand">
            <div class="logo-3f">
                {'<img src="data:image/png;base64,' + b64_logo + '" alt="Logo 3F">' if b64_logo else '<img src="logo.png" alt="Logo 3F">'}
            </div>
            <div class="brand-text">
                <strong>MUNICIPALIDAD DE TRES DE FEBRERO</strong>
                <small>Secretaría de Salud y Gestión Operativa • Análisis de Situación (ASIS)</small>
            </div>
        </div>
        <div class="nav-actions">
            <button onclick="downloadWordReport()" class="btn-naranja">
                <span>⬇ Descargar Informe de Situación (Word)</span>
            </button>
        </div>
    </nav>

    <!-- BARRA DE PESTAÑAS (TABS) FORMALES -->
    <div class="tabs-nav">
        <button type="button" onclick="switchTab('tab-resumen')" data-target="tab-resumen" id="btn-tab-resumen" class="tab-btn active">📊 Resumen Ejecutivo & Evolución</button>
        <button type="button" onclick="switchTab('tab-mapa')" data-target="tab-mapa" id="btn-tab-mapa" class="tab-btn">🗺️ Cartografía Sanitaria distrital</button>
        <button type="button" onclick="switchTab('tab-graficos')" data-target="tab-graficos" id="btn-tab-graficos" class="tab-btn">📈 Indicadores y Análisis Demográfico</button>
        <button type="button" onclick="switchTab('tab-efectores')" data-target="tab-efectores" id="btn-tab-efectores" class="tab-btn">🏥 Directorio de Efectores y Programas</button>
        <button type="button" onclick="switchTab('tab-propuestas')" data-target="tab-propuestas" id="btn-tab-propuestas" class="tab-btn">🤝 Plan de Articulación Región VII</button>
    </div>

    <!-- CONTENEDOR PRINCIPAL -->
    <div class="main-container">

        <!-- PESTAÑA 1: RESUMEN EJECUTIVO & EVOLUCIÓN EPIDEMIOLÓGICA -->
        <div id="tab-resumen" class="tab-content">
            <div class="hero">
                <span class="hero-badge">Análisis de Situación de Salud (ASIS) • Censo 2022 • Partido de Tres de Febrero</span>
                <h1>Diagnóstico de Situación Sanitaria — Partido de Tres de Febrero</h1>
                <p>
                    Plataforma interactiva de monitoreo e información georreferenciada de la <strong>Secretaría de Salud y Gestión Operativa</strong> de la <strong>Municipalidad de Tres de Febrero</strong>. Integra indicadores demográficos, epidemiológicos y de infraestructura del Censo 2022 junto con la red prestacional municipal, provincial y programas territoriales, orientada a la toma de decisiones y la articulación estratégica con la <strong>Región Sanitaria VII</strong>.
                </p>
            </div>

            <!-- TARJETAS DE INDICADORES CLAVE (KPIs) -->
            <div class="grid-4">
                <div class="kpi-card">
                    <div>
                        <div class="kpi-label">Población Total (Censo 2022)</div>
                        <div class="kpi-val">364.176 <span>hab.</span></div>
                        <div class="kpi-sub" style="color: var(--verde);">▲ +7.09% crecimiento intercensal</div>
                        <div class="kpi-detail">Densidad: 8.021,5 hab/km² (4° más densa del país)</div>
                    </div>
                    <div class="fuente-dato" style="margin-top: 12px; padding: 6px 8px; font-size: 10.5px;">
                        <strong>Fuente:</strong> INDEC. Censo Nacional de Población, Hogares y Viviendas 2022 (Resultados definitivos por partido 06840).
                    </div>
                </div>

                <div class="kpi-card naranja">
                    <div>
                        <div class="kpi-label">Envejecimiento (≥65 Años)</div>
                        <div class="kpi-val" style="color: var(--naranja-oscuro);">20,77% <span>(75.242 hab.)</span></div>
                        <div class="kpi-sub" style="color: var(--naranja-oscuro);">▲ Superior al GBA (17.5%) y PBA (18.3%)</div>
                        <div class="kpi-detail">47.171 jubilados puros + 13.369 jub/pens simultáneos</div>
                    </div>
                    <div class="fuente-dato" style="margin-top: 12px; padding: 6px 8px; font-size: 10.5px;">
                        <strong>Fuente:</strong> INDEC. Censo 2022 (Estructura demográfica por grandes grupos etarios en viviendas particulares).
                    </div>
                </div>

                <div class="kpi-card verde">
                    <div>
                        <div class="kpi-label">Mortalidad Infantil (TMI)</div>
                        <div class="kpi-val" style="color: var(--verde);">7,1 <span>‰ nacidos</span></div>
                        <div class="kpi-sub" style="color: var(--verde);">▼ Descenso histórico desde 9,2 ‰</div>
                        <div class="kpi-detail">Maternidad adolescente reducida a 7,2%</div>
                    </div>
                    <div class="fuente-dato" style="margin-top: 12px; padding: 6px 8px; font-size: 10.5px;">
                        <strong>Fuente:</strong> Dirección de Estadísticas e Información en Salud (DEIS - MSAL) y Región Sanitaria VII (Boletín Epidemiológico).
                    </div>
                </div>

                <div class="kpi-card info">
                    <div>
                        <div class="kpi-label">Cobertura Cartográfica (SIG)</div>
                        <div class="kpi-val" style="color: var(--azul-info);">457 <span>radios censales</span></div>
                        <div class="kpi-sub" style="color: var(--azul-primario);">✔️ Cobertura territorial integral distrital</div>
                        <div class="kpi-detail">Geometría oficial georreferenciada INDEC / IGN</div>
                    </div>
                    <div class="fuente-dato" style="margin-top: 12px; padding: 6px 8px; font-size: 10.5px;">
                        <strong>Fuente:</strong> Instituto Geográfico Nacional (IGN), INDEC y Cartografía Censal Oficial PBA (2026).
                    </div>
                </div>
            </div>

            <!-- GRÁFICOS INTERACTIVOS CHART.JS -->
            <div class="grid-2">
                <div class="card-panel">
                    <h2>📊 Cobertura de Salud distrital (Censo 2022)</h2>
                    <p class="desc">Distribución de la población censada en viviendas particulares según aseguramiento en salud.</p>
                    <div style="height: 260px; position: relative; width: 100%;">
                        <canvas id="chart-cobertura"></canvas>
                    </div>
                    <div class="fuente-dato">
                        <strong>Fuente de datos:</strong> INDEC. Censo Nacional de Población, Hogares y Viviendas 2022. Población en viviendas particulares según tipo de cobertura sanitaria en el Partido de Tres de Febrero (`06840`).
                    </div>
                </div>

                <div class="card-panel">
                    <h2>💧 Infraestructura y Saneamiento (3F vs GBA)</h2>
                    <p class="desc">La alta cobertura en agua (96.1%) y cloacas (92.6%) protege a la población frente a patologías infecciosas.</p>
                    <div style="height: 260px; position: relative; width: 100%;">
                        <canvas id="chart-infra"></canvas>
                    </div>
                    <div class="fuente-dato">
                        <strong>Fuente de datos:</strong> INDEC. Censo Nacional de Población, Hogares y Viviendas 2022. Hogares según acceso a servicios básicos de red de agua, cloacas, gas domiciliario e internet (Tres de Febrero vs media de los 24 partidos GBA).
                    </div>
                </div>
            </div>

            <!-- SECCIÓN NUEVA: PERFIL EPIDEMIOLÓGICO, ENCUESTAS Y CAUSAS DE MORBI-MORTALIDAD -->
            <h2 style="font-size: 20px; font-weight: 700; color: var(--azul-primario); margin: 32px 0 16px 0; border-top: 2px dashed var(--neutro-300); padding-top: 28px;">
                🧬 Perfil Epidemiológico Distrital, Encuestas de Factores de Riesgo (ENFR/UNTREF) y Morbilidad Hospitalaria
            </h2>
            <p class="desc" style="margin-bottom: 20px;">
                Diagnóstico sociosanitario ampliado a partir de encuestas nacionales biofísicas coordinadas en la región, egresos hospitalarios oficiales y relevamientos cualitativos interhospitalarios:
            </p>

            <div class="grid-2" style="margin-bottom: 24px;">
                <div class="card-panel" style="border-top: 4px solid var(--naranja);">
                    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
                        <span style="font-size: 20px;">🔬</span>
                        <h4 style="font-size: 16px; font-weight: 700; color: var(--naranja-oscuro); margin: 0;">4ª Encuesta Nacional de Factores de Riesgo (ENFR / UNTREF)</h4>
                    </div>
                    <p class="desc" style="margin-bottom: 8px;">
                        La <strong>Universidad Nacional de Tres de Febrero (UNTREF)</strong> coordinó la medición física y bioquímico-clínica en el Conurbano para la 4ª ENFR. Los hallazgos en la subregión indican una altísima prevalencia de Enfermedades Crónicas No Transmisibles (ECNT): <strong>>60% presenta sobrepeso u obesidad</strong>, el <strong>34,6% hipertensión arterial</strong> y un marcado sedentarismo. Estos datos justifican científicamente los dispositivos de actividad física y tamizaje distrital en <strong>Plazas Saludables</strong>.
                    </p>
                    <div class="fuente-dato" style="margin-top: 12px; font-size: 11px;">
                        <strong>Fuente:</strong> INDEC, Ministerio de Salud de la Nación y Universidad Nacional de Tres de Febrero (UNTREF).
                    </div>
                </div>

                <div class="card-panel" style="border-top: 4px solid var(--rojo);">
                    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
                        <span style="font-size: 20px;">🏥</span>
                        <h4 style="font-size: 16px; font-weight: 700; color: var(--rojo); margin: 0;">Egresos Hospitalarios y Principales Causas de Morbilidad</h4>
                    </div>
                    <p class="desc" style="margin-bottom: 8px;">
                        Los registros oficiales de egresos en efectores públicos distritales (Hospitales Bocalandro, Carrillo y red ambulatoria) muestran las 3 causas líderes de morbilidad grave: <strong>1º Enfermedades del Sistema Circulatorio</strong> (cardiopatías y ACV, #1 en mortalidad), <strong>2º Enfermedades del Sistema Respiratorio</strong> (neumonías/IRAB invernales en radios con NBI del norte) y <strong>3º Causas Externas y Accidentología Vial</strong> en accesos rápidos distritales (ex Ruta 8, Gral. Paz, Buen Ayre).
                    </p>
                    <div class="fuente-dato" style="margin-top: 12px; font-size: 11px;">
                        <strong>Fuente:</strong> Dirección de Estadísticas e Información en Salud (DEIS) y Dirección de Información en Salud PBA.
                    </div>
                </div>

                <div class="card-panel" style="border-top: 4px solid var(--azul-primario);">
                    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
                        <span style="font-size: 20px;">👥</span>
                        <h4 style="font-size: 16px; font-weight: 700; color: var(--azul-primario); margin: 0;">Diagnósticos ASIS Situados (Residencias FAMG / CAPS)</h4>
                    </div>
                    <p class="desc" style="margin-bottom: 8px;">
                        Estudios microterritoriales de las Residencias de Medicina General en áreas de influencia comunitaria (ej. CAPS 6 Caseros / Barrio El Mercado y Bocalandro) alertan sobre la <strong>polimedicalización en adultos mayores (20,8% previsional)</strong> y necesidades críticas en <strong>salud mental adolescente, orientación sexual y prevención de ITS</strong> en establecimientos educativos del municipio.
                    </p>
                    <div class="fuente-dato" style="margin-top: 12px; font-size: 11px;">
                        <strong>Fuente:</strong> Federación Argentina de Medicina General (FAMG) e informes de residencias interhospitalarias en CAPS.
                    </div>
                </div>

                <div class="card-panel" style="border-top: 4px solid var(--verde);">
                    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
                        <span style="font-size: 20px;">👶</span>
                        <h4 style="font-size: 16px; font-weight: 700; color: var(--verde); margin: 0;">Mortalidad Infantil (TMI) y Vigilancia Epidemiológica</h4>
                    </div>
                    <p class="desc" style="margin-bottom: 8px;">
                        La TMI en el partido mantiene una evolución descendente favorable (promedio actual <strong>7,1‰</strong>), por debajo de la media del Conurbano. Este logro se fundamenta en la captación precoz en los 13 CAPS y la capacidad resolutiva perinatal del <strong>Hospital Provincial Carrillo (~1.000 partos/año)</strong>. El reto prioritario se centra en reducir el componente neonatal (prematurez) mediante la vacunación de embarazadas y controles estables.
                    </p>
                    <div class="fuente-dato" style="margin-top: 12px; font-size: 11px;">
                        <strong>Fuente:</strong> DEIS (Ministerio de Salud de la Nación) y Observatorio del Conurbano Bonaerense (UNGS).
                    </div>
                </div>
            </div>
        </div>

        <!-- PESTAÑA 2: CARTOGRAFÍA SIG INTERACTIVA -->
        <div id="tab-mapa" class="tab-content hidden">
            <div class="card-panel">
                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 16px; margin-bottom: 16px;">
                    <div>
                        <h2>🗺️ Cartografía Georreferenciada por Radios Censales</h2>
                        <p class="desc" style="margin-bottom: 0;">
                            Visualización interactiva de los <strong>457 radios censales oficiales del Partido de Tres de Febrero</strong> y la red sanitaria completa con iconos distintivos. En celulares o computadoras, pulse el botón para ampliar a pantalla completa.
                        </p>
                    </div>
                    <div style="display: flex; gap: 10px; flex-wrap: wrap;">
                        <button onclick="toggleMapFullscreen(true)" class="btn-naranja" style="background: var(--azul-primario);">
                            <span>⛶ Ampliar Mapa a Pantalla Completa</span>
                        </button>
                    </div>
                </div>
                <div id="mapa-leaflet-container"></div>
                <div class="fuente-dato">
                    <strong>Fuente cartográfica y estadística del mapa:</strong> Cartografía Oficial de Radios Censales del Instituto Nacional de Estadística y Censos (INDEC) e Instituto Geográfico Nacional (IGN) para el Partido `06840`, integrada con microdatos del Censo 2022 sobre porcentaje de población sin cobertura formal por radio censal y relevamiento de los 19 establecimientos de salud con iconografía distintiva (Secretaría de Salud y Gestión Operativa, Municipalidad de Tres de Febrero, 2026).
                </div>
            </div>
        </div>

        <!-- PESTAÑA 3: SUITE DE GRÁFICOS ANALÍTICOS -->
        <div id="tab-graficos" class="tab-content hidden">
            <div class="card-panel" style="text-align: center; margin-bottom: 32px;">
                <h2>📈 Suite de Análisis Sociosanitario y Demográfico</h2>
                <p class="desc" style="max-width: 800px; margin: 0 auto;">
                    Análisis comparativo de determinantes sociales de la salud, distribución territorial de la dependencia pública, estructura demográfica y capacidad prestacional de la red sanitaria distrital y suprarregional.
                </p>
            </div>

            <div class="card-panel">
                <h2>1. Gradiente Territorial de Dependencia Pública por las 15 Localidades</h2>
                <p class="desc">Evidencia cómo las localidades del norte distrital (El Libertador, Churruca, Pablo Podestá, Remedios de Escalada, Loma Hermosa) concentran entre el 38% y el 43% de dependencia pública exclusiva.</p>
                <div style="text-align: center; background: var(--neutro-100); padding: 16px; border-radius: var(--radius-md); border: 1px solid var(--neutro-300);">
                    <img src="data:image/png;base64,{b64_imgs.get('grafico_dependencia_por_localidad_3f.png', '')}" alt="Dependencia por Localidad" style="max-width: 100%; height: auto; display: block; margin: 0 auto; border-radius: 8px;">
                </div>
                <div class="fuente-dato">
                    <strong>Fuente del Gráfico 1:</strong> INDEC. Censo Nacional de Población, Hogares y Viviendas 2022. Procesamiento espacial y agregación por radios censales correspondientes a cada una de las 15 localidades del Partido de Tres de Febrero en contraste con la media de la Provincia de Buenos Aires y el Gran Buenos Aires.
                </div>
            </div>

            <div class="card-panel">
                <h2>2. Pirámide Demográfica y Carga Epidemiológica del Envejecimiento</h2>
                <p class="desc">Muestra la estructura por sexo (191.214 mujeres y 172.962 varones) y destaca el 20,77% de jubilados y pensionados (75.242 hab.), argumentando la necesaria articulación PAMI - Hospital Carrillo - Hospital Bocalandro.</p>
                <div style="text-align: center; background: var(--neutro-100); padding: 16px; border-radius: var(--radius-md); border: 1px solid var(--neutro-300);">
                    <img src="data:image/png;base64,{b64_imgs.get('grafico_piramide_demografica_3f.png', '')}" alt="Piramide Demografica" style="max-width: 100%; height: auto; display: block; margin: 0 auto; border-radius: 8px;">
                </div>
                <div class="fuente-dato">
                    <strong>Fuente del Gráfico 2:</strong> INDEC. Censo Nacional de Población, Hogares y Viviendas 2022. Población censada en viviendas particulares por sexo registrado y grupos quinquenales de edad en Tres de Febrero (`06840`) y proyecciones de envejecimiento de la Dirección Provincial de Estadística (DPE PBA).
                </div>
            </div>

            <div class="card-panel">
                <h2>3. Comparativa de Infraestructura Sanitaria Básica (3F vs GBA)</h2>
                <p class="desc">Tres de Febrero sobresale netamente sobre el conurbano con 96,1% en acceso a agua corriente y 92,6% a cloacas de red, blindando la salud de la infancia frente a enteropatías e infecciones bacterianas.</p>
                <div style="text-align: center; background: var(--neutro-100); padding: 16px; border-radius: var(--radius-md); border: 1px solid var(--neutro-300);">
                    <img src="data:image/png;base64,{b64_imgs.get('grafico_cobertura_vs_infraestructura_3f.png', '')}" alt="Infraestructura Sanitaria" style="max-width: 100%; height: auto; display: block; margin: 0 auto; border-radius: 8px;">
                </div>
                <div class="fuente-dato">
                    <strong>Fuente del Gráfico 3:</strong> INDEC. Censo Nacional de Población, Hogares y Viviendas 2022. Indicadores habitacionales y de saneamiento básico en hogares particulares del Partido de Tres de Febrero frente al promedio consolidado de los 24 partidos del Gran Buenos Aires.
                </div>
            </div>

            <div class="card-panel">
                <h2>4. Estructura Prestacional y Capacidad de la Red Sanitaria</h2>
                <p class="desc">Sintetiza la red del primer nivel (13 CAPS + CEMAR + 2 Monovalentes) y los efectores de agudos provinciales y suprarregionales (~350 camas entre H. Carrillo, H. Bocalandro y UPA 16).</p>
                <div style="text-align: center; background: var(--neutro-100); padding: 16px; border-radius: var(--radius-md); border: 1px solid var(--neutro-300);">
                    <img src="data:image/png;base64,{b64_imgs.get('grafico_capacidad_efectores_3f.png', '')}" alt="Efectores Sanitaros" style="max-width: 100%; height: auto; display: block; margin: 0 auto; border-radius: 8px;">
                </div>
                <div class="fuente-dato">
                    <strong>Fuente del Gráfico 4:</strong> Relevamiento Operativo de la Secretaría de Salud y Gestión Operativa (Municipalidad de Tres de Febrero, 2026), Catálogo Nacional de Establecimientos de Salud (SISA / Refes) e informes de gestión de la Dirección de Hospitales (Ministerio de Salud de la Provincia de Buenos Aires - Región VII).
                </div>
            </div>
        </div>

        <!-- PESTAÑA 4: RED DE EFECTORES & PROGRAMAS COMUNITARIOS -->
        <div id="tab-efectores" class="tab-content hidden">
            <!-- PROGRAMAS COMUNITARIOS EN CAPS -->
            <div class="card-panel" style="background: var(--azul-oscuro); color: #fff; border-color: var(--azul-primario);">
                <h2 style="color: #fff;">🌱 Programas de Salud Comunitaria y Prevención en CAPS / CEMAR</h2>
                <p class="desc" style="color: var(--azul-claro); margin-bottom: 8px;">
                    Según la evaluación territorial de los equipos de salud, los centros sanitarios municipales no solo atienden patología aguda, sino que sostienen <strong>9 dispositivos de promoción y prevención sociosanitaria</strong>, sumando el sistema de <strong>Telemedicina 24 hs</strong>:
                </p>
                <div class="programas-grid">
                    <div class="prog-badge">🎲 1. Ludotecas</div>
                    <div class="prog-badge">🧠 2. Estimulación Cognitiva</div>
                    <div class="prog-badge">💬 3. Habilidades Socio-emocionales</div>
                    <div class="prog-badge">💜 4. Talleres Mujeres y Diversidades</div>
                    <div class="prog-badge">🥬 5. Huertas Comunitarias</div>
                    <div class="prog-badge">👶 6. Grupos de Crianza</div>
                    <div class="prog-badge">📚 7. Alfabetización</div>
                    <div class="prog-badge">🏡 8. Orientación a Familias</div>
                    <div class="prog-badge">🚶 9. Caminatas Saludables</div>
                    <div class="prog-badge highlight">📱 Telemedicina las 24 hs</div>
                </div>
                <div class="fuente-dato" style="background: rgba(255, 255, 255, 0.08); color: var(--azul-suave); border-left-color: var(--naranja);">
                    <strong style="color: #fff;">Fuente operativa de programas:</strong> Relevamiento territorial, Evaluación de Admisión Previa y Memoria Institucional del Primer Nivel de Atención y Salud Comunitaria (Secretaría de Salud y Gestión Operativa, Municipalidad de Tres de Febrero, 2026).
                </div>
            </div>

            <!-- DIRECTORIO DE HOSPITALES PROVINCIALES, NACIONAL Y MONOVALENTES -->
            <h2 style="font-size: 20px; font-weight: 700; color: var(--azul-primario); margin: 24px 0 12px 0;">🏥 Directorio de Efectores Provinciales (Región VII), Nacional y Municipales</h2>
            <div class="efectores-grid">
                <!-- BOCALANDRO -->
                <div class="efector-card rojo">
                    <span class="efector-tag rojo">Provincial • Región VII</span>
                    <h4>H.Z.G.A. Dr. Carlos A. Bocalandro</h4>
                    <p class="loc">📍 Av. Eva Perón Km 20,5 N° 9100, Loma Hermosa</p>
                    <p class="txt">Inaugurado en 1996 (~175 camas). Alta complejidad: cirugía videolaparoscópica, endoscopía, neonatología y oncoginecología. <strong>Registra ~220.000 consultas externas y ~2.000 nacimientos anuales.</strong></p>
                </div>

                <!-- CARRILLO -->
                <div class="efector-card rojo">
                    <span class="efector-tag rojo">Provincial • Región VII (Base SIES)</span>
                    <h4>H.Z.G.A. Prof. Dr. Ramón Carrillo</h4>
                    <p class="loc">📍 Hipólito Yrigoyen 1051, Ciudadela</p>
                    <p class="txt">Cuenta con entre 164 y 200 camas. Maternidad y neonatología (<strong>entre 900 y 1.200 partos anuales</strong>). Es la <strong>Sede Operativa de la Base SIES</strong> de la Región Sanitaria VII.</p>
                </div>

                <!-- POSADAS -->
                <div class="efector-card naranja">
                    <span class="efector-tag naranja">Nacional • Referencia Suprarregional</span>
                    <h4>Hospital Nacional Prof. A. Posadas</h4>
                    <p class="loc">📍 Av. Pte. Illia s/n, El Palomar (Morón, limítrofe)</p>
                    <p class="txt">Hospital Público de Gestión Descentralizada con <strong>~488 camas</strong>. Área de influencia directa en 15 partidos de RS V, VII y XII; efector máximo receptor de derivaciones hipercríticas desde 3F.</p>
                </div>

                <!-- CEMAR Y MONOVALENTES -->
                <div class="efector-card">
                    <span class="efector-tag">Municipal • 2° Nivel Ambulatorio</span>
                    <h4>CEMAR Caseros (Especialidades)</h4>
                    <p class="loc">📍 Labardén y Labardén, Caseros Centro</p>
                    <p class="txt">Centro de Referencia para consultas derivadas por los 13 CAPS en Cardiología, Endocrinología, Neumonología, Ecografías, Trabajo Social y Ginecología.</p>
                </div>

                <div class="efector-card">
                    <span class="efector-tag">Municipal • 2 Monovalentes</span>
                    <h4>Hospital Odontológico y Oftalmológico</h4>
                    <p class="loc">📍 Caseros Centro (Dr. Norberto Di Próspero)</p>
                    <p class="txt">Atención especializada distrital en salud bucal de alta complejidad (cirugía maxilofacial, endodoncia) y centro integral de ojos y cirugías oculares.</p>
                </div>

                <div class="efector-card rojo">
                    <span class="efector-tag rojo">Provincial • Urgencias 24hs</span>
                    <h4>UPA 24 hs N° 16 Martín Coronado</h4>
                    <p class="loc">📍 Perón y San Lorenzo, Martín Coronado</p>
                    <p class="txt">Unidad de Pronta Atención 24 hs. Estabiliza emergencias intermedias e interconecta los CAPS centrales con las guardias hospitalarias provinciales.</p>
                </div>
            </div>

            <!-- LISTADO DE LOS 13 CAPS MUNICIPALES -->
            <h2 style="font-size: 20px; font-weight: 700; color: var(--azul-primario); margin: 28px 0 12px 0;">📍 Centros de Atención Primaria de la Salud (13 CAPS Municipales)</h2>
            <div class="efectores-grid">
                <div class="efector-card" style="padding: 16px;"><h4 style="font-size: 14px;">CAPS 1 • Ciudadela Norte</h4><p class="loc" style="margin: 0;">Gazeta de Bs. As. 3550</p></div>
                <div class="efector-card" style="padding: 16px;"><h4 style="font-size: 14px;">CAPS 2 • José Ingenieros</h4><p class="loc" style="margin: 0;">Alvear 2790</p></div>
                <div class="efector-card" style="padding: 16px;"><h4 style="font-size: 14px;">CAPS 3 • Sáenz Peña</h4><p class="loc" style="margin: 0;">Av. América 651</p></div>
                <div class="efector-card" style="padding: 16px;"><h4 style="font-size: 14px;">CAPS 4 • Villa Raffo</h4><p class="loc" style="margin: 0;">San Pedro 1350</p></div>
                <div class="efector-card" style="padding: 16px;"><h4 style="font-size: 14px;">CAPS 5 • Santos Lugares</h4><p class="loc" style="margin: 0;">Patagonia y Pje. A y B</p></div>
                <div class="efector-card" style="padding: 16px;"><h4 style="font-size: 14px;">CAPS 6 • Caseros Centro</h4><p class="loc" style="margin: 0;">Labardén y Labardén</p></div>
                <div class="efector-card" style="padding: 16px;"><h4 style="font-size: 14px;">CAPS 7 • Ciudad Jardín</h4><p class="loc" style="margin: 0;">Matienzo y Wernicke</p></div>
                <div class="efector-card" style="padding: 16px;"><h4 style="font-size: 14px;">CAPS 8 • Villa Bosch</h4><p class="loc" style="margin: 0;">Miguel Ángel y Quintana</p></div>
                <div class="efector-card" style="padding: 16px;"><h4 style="font-size: 14px;">CAPS 9 • Martín Coronado</h4><p class="loc" style="margin: 0;">San Lorenzo 1401</p></div>
                <div class="efector-card naranja" style="padding: 16px;"><h4 style="font-size: 14px; color: var(--naranja-oscuro);">CAPS 10 (Prioridad 1) • Loma Hermosa</h4><p class="loc" style="margin: 0;">Gabino Ezeiza 9250</p></div>
                <div class="efector-card naranja" style="padding: 16px;"><h4 style="font-size: 14px; color: var(--naranja-oscuro);">CAPS 11 (Prioridad 1) • R. de Escalada</h4><p class="loc" style="margin: 0;">Av. Pérez Galdós y San Juan</p></div>
                <div class="efector-card naranja" style="padding: 16px;"><h4 style="font-size: 14px; color: var(--naranja-oscuro);">CAPS 12 (Prioridad 1) • Pablo Podestá</h4><p class="loc" style="margin: 0;">Firpo y San Martín</p></div>
                <div class="efector-card naranja" style="padding: 16px;"><h4 style="font-size: 14px; color: var(--naranja-oscuro);">CAPS 13 (Prioridad 1) • Churruca</h4><p class="loc" style="margin: 0;">Iguazú y Salta</p></div>
            </div>
            </div>

            <!-- SECCIÓN NUEVA: CAMPAÑAS SANITARIAS, PROGRAMAS MUNICIPALES Y CANALES DIGITALES DE ATENCIÓN -->
            <h2 style="font-size: 20px; font-weight: 700; color: var(--azul-primario); margin: 36px 0 16px 0; border-top: 2px dashed var(--neutro-300); padding-top: 28px;">
                📢 Campañas Sanitarias, Programas Municipales y Canales de Atención Distrital
            </h2>
            <p class="desc" style="margin-bottom: 20px;">
                Estrategias de atención primaria, prevención epidemiológica y autogestión ciudadana implementadas activamente por la <strong>Secretaría de Salud y Gestión Operativa</strong> del Municipio de Tres de Febrero (disponibles en <a href="https://www.tresdefebrero.gov.ar/salud/" target="_blank" style="color: var(--azul-primario); font-weight: 700;">tresdefebrero.gov.ar/salud</a>):
            </p>

            <div class="grid-2" style="margin-bottom: 24px;">
                <div class="card-panel" style="border-top: 4px solid var(--azul-primario);">
                    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
                        <span style="font-size: 20px;">📲</span>
                        <h4 style="font-size: 16px; font-weight: 700; color: var(--azul-primario); margin: 0;">Portal Autogestión de Turnos (Mi3F) & Telemedicina</h4>
                    </div>
                    <p class="desc" style="margin-bottom: 8px;">
                        Plataforma digital para la reserva de turnos protegidos en especialidades y medicina general en los 13 CAPS municipales (<a href="https://turnos.tresdefebrero.gob.ar/home" target="_blank" style="color: var(--naranja-oscuro); font-weight: 600;">Mi3F / turnos.tresdefebrero.gob.ar</a>). Se complementa con consultorios virtuales de <strong>Telemedicina</strong> para resolver demandas de baja complejidad sin desplazamientos físicos y un Call Center distrital continuo.
                    </p>
                </div>

                <div class="card-panel" style="border-top: 4px solid var(--rojo);">
                    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
                        <span style="font-size: 20px;">🚑</span>
                        <h4 style="font-size: 16px; font-weight: 700; color: var(--rojo); margin: 0;">SAME Tres de Febrero (107 Municipal) & SIES</h4>
                    </div>
                    <p class="desc" style="margin-bottom: 8px;">
                        Sistema de Atención Médica de Emergencias prehospitalario propio, con despacho permanente a través del número <strong>107</strong>. Cuenta con unidades de terapia intensiva móvil (UTIM) georreferenciadas que trabajan en red con las guardias de agudos provinciales y la Base SIES R7 del Hospital Carrillo.
                    </p>
                </div>

                <div class="card-panel" style="border-top: 4px solid var(--verde);">
                    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
                        <span style="font-size: 20px;">💉</span>
                        <h4 style="font-size: 16px; font-weight: 700; color: var(--verde); margin: 0;">Campañas de Vacunación Integral (#YoPongoElBrazo)</h4>
                    </div>
                    <p class="desc" style="margin-bottom: 8px;">
                        Estrategia continua de inmunización comunitaria (<a href="https://www.tresdefebrero.gov.ar/yopongoelbrazo/" target="_blank" style="color: var(--verde); font-weight: 600;">#YoPongoElBrazo</a>) aplicada en los 13 CAPS y rondas móviles. Incluye el <strong>Esquema de Calendario Nacional</strong>, la dosis extra de <strong>Vacuna Triple Viral</strong> (Sarampión, Rubéola, Paperas), vacunación prioritaria para embarazadas (VRS, Triple Bacteriana Acelular, Antigripal) y prevención contra Hepatitis B/C y Tuberculosis.
                    </p>
                </div>

                <div class="card-panel" style="border-top: 4px solid var(--naranja);">
                    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
                        <span style="font-size: 20px;">🏃</span>
                        <h4 style="font-size: 16px; font-weight: 700; color: var(--naranja-oscuro); margin: 0;">3F Cuida tu Salud & Plazas Saludables</h4>
                    </div>
                    <p class="desc" style="margin-bottom: 8px;">
                        Programa distrital descentralizado en parques y plazas de las distintas localidades (<a href="https://www.tresdefebrero.gov.ar/3fcuidatusalud/" target="_blank" style="color: var(--naranja-oscuro); font-weight: 600;">3F Cuida tu Salud</a> / <a href="https://www.tresdefebrero.gov.ar/salud/plazassaludables/" target="_blank" style="color: var(--naranja-oscuro); font-weight: 600;">Plazas Saludables</a>). Ofrece controles clínicos espontáneos de tensión arterial, glucemia, peso, índice de masa corporal (IMC) y consejería nutricional activa para frenar enfermedades crónicas no transmisibles.
                    </p>
                </div>

                <div class="card-panel" style="border-top: 4px solid var(--azul-info);">
                    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
                        <span style="font-size: 20px;">🦟</span>
                        <h4 style="font-size: 16px; font-weight: 700; color: var(--azul-info); margin: 0;">Vigilancia Arbovirosis (Dengue) & Zoonosis</h4>
                    </div>
                    <p class="desc" style="margin-bottom: 8px;">
                        Plan integral de lucha contra el vector del <strong>Dengue, Zika y Chikungunya</strong> (<a href="https://www.tresdefebrero.gov.ar/dengue/" target="_blank" style="color: var(--azul-info); font-weight: 600;">Vigilancia y Descacharrado</a>) con fumigación territorial y operativos de control de foco. Se integra con las campañas gratuitas de <strong>Zoonosis ("Mascotas de 3F")</strong> para vacunación antirrábica y esterilización quirúrgica itinerante.
                    </p>
                </div>

                <div class="card-panel" style="border-top: 4px solid #6b21a8;">
                    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
                        <span style="font-size: 20px;">🩺</span>
                        <h4 style="font-size: 16px; font-weight: 700; color: #6b21a8; margin: 0;">Prevención de Enfermedades Crónicas y Tamizaje Especializado</h4>
                    </div>
                    <p class="desc" style="margin-bottom: 8px;">
                        Atención gratuita e integral para pacientes diabéticos (<strong>PRODIABA</strong> con provisión virtual continua de insumos y fármacos), tamizaje temprano del cáncer de cuello uterino (PAP y Test de VPH en todos los CAPS), talleres de salud integral para adolescentes en establecimientos educativos, y diagnóstico odontológico digitalizado mediante <strong>Pantomógrafo de Alta Complejidad</strong> en el Hospital Di Próspero.
                    </p>
                </div>
            </div>

            <div class="fuente-dato" style="margin-top: 24px;">
                <strong>Fuente del Directorio de Red Sanitaria y Programas:</strong> Sistema Integrado de Información Sanitaria Argentino (SISA - Ministerio de Salud de la Nación), Registro Federal de Establecimientos de Salud (Refes), Dirección de Hospitales de Región Sanitaria VII (PBA) y Portal Oficial de la Secretaría de Salud y Gestión Operativa de la Municipalidad de Tres de Febrero (2026 - <a href="https://www.tresdefebrero.gov.ar/salud/" target="_blank">tresdefebrero.gov.ar/salud</a>).
            </div>
        </div>

        <!-- PESTAÑA 5: PLAN DE ACCIÓN REGIÓN VII -->
        <div id="tab-propuestas" class="tab-content hidden">
            <div class="hero" style="background: linear-gradient(135deg, var(--azul-primario) 0%, #1a4f8b 100%); margin-bottom: 24px;">
                <span class="hero-badge" style="background: #fff; color: var(--azul-primario);">Plan Operativo 2026–2027</span>
                <h1>Propuestas de Articulación con la Región Sanitaria VII</h1>
                <p>Lineamientos institucionales y operativos diseñados para fortalecer la continuidad de cuidados entre el primer nivel municipal y los hospitales de agudos de la Provincia de Buenos Aires.</p>
            </div>

            <div class="grid-2">
                <div class="card-panel">
                    <h2 style="font-size: 18px;">1. Interconsultas y Turnos Protegidos (SIREC 3F – Región VII)</h2>
                    <p class="desc">Formalización de un canal digital ágil entre los 13 CAPS municipales y los consultorios de especialidades de los Hospitales Bocalandro y Carrillo para encauzar a los pacientes sin cobertura formal (27,2% distrital).</p>
                </div>

                <div class="card-panel" style="border-left: 4px solid var(--naranja);">
                    <h2 style="font-size: 18px; color: var(--naranja-oscuro);">2. Operativos Integrales en el Corredor Norte</h2>
                    <p class="desc">Conformación de rondas sociosanitarias intersectoriales en los radios críticos de El Libertador, Churruca, Pablo Podestá, Remedios de Escalada y Loma Hermosa (donde la dependencia pública supera el 40%).</p>
                </div>

                <div class="card-panel">
                    <h2 style="font-size: 18px;">3. Red Gerontológica Regional (PAMI + Hospitales + Municipio)</h2>
                    <p class="desc">Articulación permanente dirigida al 20,8% de población jubilada distrital (75.242 personas), coordinando los talleres de estimulación cognitiva en los CAPS/CEMAR con las prestaciones interconsultoras de PAMI y servicios de crónicos provinciales.</p>
                </div>

                <div class="card-panel" style="border-left: 4px solid var(--verde);">
                    <h2 style="font-size: 18px; color: var(--verde);">4. Interoperabilidad de Despacho en Emergencias (107 – SIES R7)</h2>
                    <p class="desc">Conexión directa entre el Centro de Monitoreo municipal (107 / Telemedicina) y la Base Operativa SIES R7 centralizada en el Hospital Carrillo de Ciudadela, optimizando la respuesta en código rojo en la vía pública.</p>
                </div>
            </div>
            <div class="fuente-dato">
                <strong>Referencia de lineamientos estratégicos:</strong> Plan de Articulación y Acuerdos de Gestión Intergubernamental para el Área Metropolitana de Buenos Aires (AMBA) consensuados entre la Secretaría de Salud de la Municipalidad de Tres de Febrero y la Dirección de la Región Sanitaria VII (Ministerio de Salud de la Provincia de Buenos Aires, 2026).
            </div>
        </div>

    </div>

    <!-- FOOTER MUNICIPAL FORMAL -->
    <footer>
        <div class="footer-content">
            <p class="inst">MUNICIPALIDAD DE TRES DE FEBRERO — SECRETARÍA DE SALUD Y GESTIÓN OPERATIVA</p>
            <p class="sub">Sistema de Información Georreferenciada (SIG) • Análisis de Situación de Salud distrital • Región Sanitaria VII</p>
        </div>
    </footer>

    <!-- LOGICA JS E INICIALIZACIÓN DE GRÁFICOS DYNAMICOS Y MAPA LEAFLET -->
    <script>
        const geojsonData3F = {geojson_json_str};
        const b64DocxData = "{b64_docx}";

        function switchTab(tabId) {{
            document.querySelectorAll('.tab-content').forEach(el => el.classList.add('hidden'));
            document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
            const targetEl = document.getElementById(tabId);
            const btnEl = document.getElementById('btn-' + tabId);
            if (targetEl) targetEl.classList.remove('hidden');
            if (btnEl) btnEl.classList.add('active');
            if (tabId === 'tab-mapa') {{
                setTimeout(() => {{ if (window.mapaLeaflet) window.mapaLeaflet.invalidateSize(); }}, 200);
            }}
        }}

        document.addEventListener('DOMContentLoaded', function() {{
            document.querySelectorAll('.tab-btn').forEach(btn => {{
                btn.addEventListener('touchend', function(e) {{
                    e.preventDefault();
                    const tabId = this.getAttribute('data-target');
                    if (tabId) switchTab(tabId);
                }}, {{passive: false}});
                btn.addEventListener('click', function(e) {{
                    const tabId = this.getAttribute('data-target');
                    if (tabId) switchTab(tabId);
                }});
            }});
        }});

        function openExternalMap(e) {{
            if (e) e.preventDefault();
            try {{
                let win = window.open("mapa_interactivo_salud_3f.html", "_blank");
                if (!win || win.closed || typeof win.closed == 'undefined') {{
                    win = window.open("salidas/mapa_interactivo_salud_3f.html", "_blank");
                }}
                if (!win || win.closed || typeof win.closed == 'undefined') {{
                    toggleMapFullscreen(true);
                }}
            }} catch(err) {{
                toggleMapFullscreen(true);
            }}
        }}

        function toggleMapFullscreen(enable) {{
            const mapEl = document.getElementById('mapa-leaflet-container');
            const closeBtn = document.getElementById('btn-close-fullscreen');
            if (!mapEl) return;
            if (enable) {{
                mapEl.classList.add('fullscreen-active');
                if (closeBtn) closeBtn.style.display = 'flex';
                document.body.style.overflow = 'hidden';
            }} else {{
                mapEl.classList.remove('fullscreen-active');
                if (closeBtn) closeBtn.style.display = 'none';
                document.body.style.overflow = 'auto';
            }}
            setTimeout(() => {{ if (window.mapaLeaflet) window.mapaLeaflet.invalidateSize(); }}, 250);
        }}

        function downloadWordReport() {{
            try {{
                if (b64DocxData && b64DocxData.length > 100) {{
                    const byteCharacters = atob(b64DocxData);
                    const byteNumbers = new Array(byteCharacters.length);
                    for (let i = 0; i < byteCharacters.length; i++) {{
                        byteNumbers[i] = byteCharacters.charCodeAt(i);
                    }}
                    const byteArray = new Uint8Array(byteNumbers);
                    const blob = new Blob([byteArray], {{ type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document" }});
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement("a");
                    a.href = url;
                    a.download = "informe_situacion_salud_tres_de_febrero_COMPLETO.docx";
                    document.body.appendChild(a);
                    a.click();
                    setTimeout(() => {{ document.body.removeChild(a); URL.revokeObjectURL(url); }}, 150);
                }} else {{
                    const a = document.createElement("a");
                    a.href = "informe_situacion_salud_tres_de_febrero_COMPLETO.docx";
                    a.download = "informe_situacion_salud_tres_de_febrero_COMPLETO.docx";
                    document.body.appendChild(a);
                    a.click();
                    setTimeout(() => {{ document.body.removeChild(a); }}, 150);
                }}
            }} catch(e) {{
                console.warn("Fallo descarga Blob, reintentando por enlace directo:", e);
                window.location.href = "informe_situacion_salud_tres_de_febrero_COMPLETO.docx";
            }}
        }}

        window.addEventListener('DOMContentLoaded', () => {{
            // 1. Gráfico Cobertura
            const ctxCob = document.getElementById('chart-cobertura').getContext('2d');
            new Chart(ctxCob, {{
                type: 'doughnut',
                data: {{
                    labels: ['Obra Social / Prepaga (70.76%)', 'Exclusivo Público (27.20%)', 'Planes Estatales (2.04%)'],
                    datasets: [{{
                        data: [256381, 98540, 7398],
                        backgroundColor: ['#163C68', '#F69321', '#13B423'],
                        borderWidth: 2,
                        borderColor: '#ffffff'
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        legend: {{ position: 'bottom', labels: {{ font: {{ family: 'Montserrat', size: 12, weight: 'bold' }} }} }},
                        tooltip: {{ callbacks: {{ label: (ctx) => ` ${{ctx.label.split('(')[0]}}: ${{ctx.raw.toLocaleString('es-AR')}} hab.` }} }}
                    }}
                }}
            }});

            // 2. Gráfico Infraestructura
            const ctxInf = document.getElementById('chart-infra').getContext('2d');
            new Chart(ctxInf, {{
                type: 'bar',
                data: {{
                    labels: ['Agua de Red', 'Cloacas', 'Gas de Red', 'Internet'],
                    datasets: [
                        {{
                            label: 'Tres de Febrero (06840)',
                            data: [96.1, 92.6, 89.4, 87.5],
                            backgroundColor: '#163C68',
                            borderRadius: 6
                        }},
                        {{
                            label: 'Promedio GBA',
                            data: [78.4, 61.2, 72.1, 74.8],
                            backgroundColor: '#B1B7BE',
                            borderRadius: 6
                        }}
                    ]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {{
                        y: {{ beginAtZero: true, max: 100, ticks: {{ callback: (v) => v + '%' }} }}
                    }},
                    plugins: {{
                        legend: {{ position: 'bottom', labels: {{ font: {{ family: 'Montserrat', size: 12, weight: 'bold' }} }} }}
                    }}
                }}
            }});

            // 3. Inicializar Mapa Leaflet con los 457 polígonos e ICONOS CIRCULARES DE HOSPITALES / CAPS
            const mapContainer = document.getElementById('mapa-leaflet-container');
            if (mapContainer && geojsonData3F && geojsonData3F.features && geojsonData3F.features.length > 0) {{
                const isMobile = window.innerWidth <= 600;
                const map = L.map('mapa-leaflet-container').setView([-34.595, -58.565], isMobile ? 12 : 13);
                L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
                    attribution: '&copy; OpenStreetMap & INDEC/IGN/PBA'
                }}).addTo(map);

                function getColor(p) {{
                    return p > 40 ? '#b30000' :
                           p > 35 ? '#e34a33' :
                           p > 30 ? '#fc8d59' :
                           p > 24 ? '#fdbb84' :
                           p > 18 ? '#fdd49e' : '#fef0d9';
                }}

                L.geoJSON(geojsonData3F, {{
                    style: function(feature) {{
                        const pct = parseFloat(feature.properties.pct_sin_cobertura_exclusivo_publico) || 27.2;
                        return {{
                            fillColor: getColor(pct),
                            weight: 0.8,
                            opacity: 1,
                            color: '#163C68',
                            fillOpacity: 0.75
                        }};
                    }},
                    onEachFeature: function(feature, layer) {{
                        const p = feature.properties;
                        const popupWidth = window.innerWidth <= 480 ? '190px' : '230px';
                        const popupText = `
                            <div style="font-family:'Montserrat',sans-serif; width:${{popupWidth}};">
                                <h4 style="margin:0; color:#163C68; font-size:13px;"><b>Radio: ${{p.codigo_radio || 'N/D'}}</b></h4>
                                <p style="margin:3px 0; font-size:11px;"><b>Localidad:</b> ${{p.localidad || 'Tres de Febrero'}}</p>
                                <p style="margin:3px 0; font-size:11px;"><b>Población:</b> ${{p.poblacion_viviendas_particulares || 950}} hab.</p>
                                <p style="margin:3px 0; font-size:11px;"><b>Sin Cobertura (Público):</b> <span style="color:#DB3D3D; font-weight:bold;">${{parseFloat(p.pct_sin_cobertura_exclusivo_publico).toFixed(1)}}%</span></p>
                                <p style="margin:3px 0; font-size:11px;"><b>Prioridad:</b> ${{p.prioridad_sanitaria_caps || 'Media'}}</p>
                            </div>
                        `;
                        layer.bindPopup(popupText);
                    }}
                }}).addTo(map);

                // FUNCIÓN HELPER PARA CREAR ICONOS CIRCULARES OFICIALES (L.divIcon)
                function createCustomIcon(iconSymbol, bgColor, size=34) {{
                    return L.divIcon({{
                        className: 'custom-leaflet-icon',
                        html: `<div class="icon-efector-div" style="width: ${{size}}px; height: ${{size}}px; background: ${{bgColor}}; color: #fff;">${{iconSymbol}}</div>`,
                        iconSize: [size, size],
                        iconAnchor: [size/2, size/2],
                        popupAnchor: [0, -size/2]
                    }});
                }}

                // AGREGAR LOS EFECTORES SANITARIOS PRINCIPALES CON SUS ICONOS, COLORES Y COORDENADAS EXACTAS VERIFICADAS
                const efectoresList = [
                    ["H.Z.G.A. Dr. Carlos A. Bocalandro", -34.5631, -58.6024, "Hospital Provincial R7 (~175 camas)", "🏥", "#DB3D3D", 38],
                    ["H.Z.G.A. Prof. Dr. Ramón Carrillo (Base SIES)", -34.6277, -58.5556, "Hospital Provincial R7 (164-200 camas)", "🏥", "#DB3D3D", 38],
                    ["Hospital Nacional Prof. A. Posadas", -34.6290, -58.5749, "Hospital Nacional Suprarregional (~488 camas)", "🏥", "#F69321", 38],
                    ["UPA 24 hs N° 16 Martín Coronado", -34.5855, -58.5845, "Unidad de Pronta Atención Provincial", "🚨", "#b30000", 36],
                    ["CEMAR Caseros (Especialidades)", -34.6042, -58.5604, "Centro de Referencia Municipal 2° Nivel", "🩺", "#0E2A49", 36],
                    ["Hospital Odontológico y Oftalmológico Di Próspero", -34.6036, -58.5644, "Hospitales Monovalentes Municipales", "🦷", "#3B93F7", 36],
                    ["CAPS 1 - Ciudadela Norte", -34.6378, -58.5437, "CAPS Municipal (Atención Primaria)", "📍", "#163C68", 30],
                    ["CAPS 2 - José Ingenieros", -34.6172, -58.5411, "CAPS Municipal (Atención Primaria)", "📍", "#163C68", 30],
                    ["CAPS 3 - Sáenz Peña", -34.6020, -58.5281, "CAPS Municipal (Atención Primaria)", "📍", "#163C68", 30],
                    ["CAPS 4 - Villa Raffo", -34.6071, -58.5301, "CAPS Municipal (Atención Primaria)", "📍", "#163C68", 30],
                    ["CAPS 5 - Santos Lugares", -34.6016, -58.5401, "CAPS Municipal (Atención Primaria)", "📍", "#163C68", 30],
                    ["CAPS 6 - Caseros Centro", -34.6045, -58.5610, "CAPS Municipal (Atención Primaria)", "📍", "#163C68", 30],
                    ["CAPS 7 - Ciudad Jardín", -34.5919, -58.5909, "CAPS Municipal (Atención Primaria)", "📍", "#163C68", 30],
                    ["CAPS 8 - Villa Bosch", -34.5920, -58.5725, "CAPS Municipal (Atención Primaria)", "📍", "#163C68", 30],
                    ["CAPS 9 - Martín Coronado", -34.5842, -58.5852, "CAPS Municipal (Atención Primaria)", "📍", "#163C68", 30],
                    ["CAPS 10 - Loma Hermosa", -34.5627, -58.6128, "CAPS Municipal (Corredor Norte - Prioridad 1)", "📍", "#163C68", 30],
                    ["CAPS 11 - Remedios de Escalada", -34.5696, -58.6212, "CAPS Municipal (Corredor Norte - Prioridad 1)", "📍", "#163C68", 30],
                    ["CAPS 12 - Pablo Podestá", -34.5797, -58.6133, "CAPS Municipal (Corredor Norte - Prioridad 1)", "📍", "#163C68", 30],
                    ["CAPS 13 - Churruca / El Libertador", -34.5589, -58.6204, "CAPS Municipal (Corredor Norte - Prioridad 1)", "📍", "#163C68", 30]
                ];

                efectoresList.forEach(e => {{
                    const markerIcon = createCustomIcon(e[4], e[5], e[6]);
                    L.marker([e[1], e[2]], {{ icon: markerIcon }}).addTo(map).bindPopup(`
                        <div style="font-family:'Montserrat',sans-serif; width:220px;">
                            <h4 style="margin:0 0 4px 0; color:${{e[5]}}; font-size:13px;"><b>${{e[0]}}</b></h4>
                            <p style="margin:0; font-size:11.5px; color:#2F4054;">${{e[3]}}</p>
                        </div>
                    `);
                }});

                window.mapaLeaflet = map;
            }}
        }});
    </script>
</body>
</html>"""
    
    html_index = os.path.join(base_dir, 'index.html')
    with open(html_salidas, 'w', encoding='utf-8') as f:
        f.write(html_content)
    with open(html_root, 'w', encoding='utf-8') as f:
        f.write(html_content)
    with open(html_index, 'w', encoding='utf-8') as f:
        f.write(html_content)
        
    print(f"[¡ÉXITO HTML GENERADO CON PANTALLA COMPLETA MÓVIL, ICONOS OFICIALES Y DESCARGA BLOB!]\n -> {html_root}\n -> {html_salidas}\n -> {html_index}")

if __name__ == '__main__':
    generar_tablero_self_contained()
