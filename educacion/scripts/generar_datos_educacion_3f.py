# -*- coding: utf-8 -*-
"""
generar_datos_educacion_3f.py
Consolidación estadística del Censo Nacional 2022 (INDEC) para el Partido de Tres de Febrero (06840),
Indicadores de TIC / Brecha Digital en el hogar, y generación de visualizaciones analíticas
para el ASIS-Educativo de Tres de Febrero.
"""

import os
import json
import matplotlib.pyplot as plt
import numpy as np

# Configurar estilo visual de gráficos
plt.rcParams['font.sans-serif'] = 'Segoe UI', 'Helvetica', 'Arial', 'sans-serif'
plt.rcParams['axes.edgecolor'] = '#CBD5E1'
plt.rcParams['axes.linewidth'] = 1.0

# Directorios de salida
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SALIDAS_DIR = os.path.join(BASE_DIR, 'salidas')
os.makedirs(SALIDAS_DIR, exist_ok=True)

# ---------------------------------------------------------
# 1. BASES DE DATOS ESTADÍSTICAS OFICIALES (CENSO 2022 INDEC)
# ---------------------------------------------------------

DATOS_DEMOGRAFICOS_3F = {
    "poblacion_total": 364176,
    "mujeres": 191214,
    "varones": 172962,
    "porcentaje_mujeres": 52.5,
    "porcentaje_varones": 47.5,
    "densidad_poblacional": 8021.5, # hab/km2
    "radios_censales": 457
}

# Condición de asistencia escolar por franja etaria (%) - Censo 2022
ASISTENCIA_POR_EDAD = {
    "edades": ["3 a 5 años\n(Inicial)", "6 a 11 años\n(Primario)", "12 a 17 años\n(Secundario)", "18 a 24 años\n(Superior/Jóvenes)", "25 a 29 años\n(Jóvenes adult.)", "30 años y más\n(Adultos)"],
    "asiste": [68.2, 99.1, 95.4, 48.6, 22.4, 4.8],
    "asistio_pasado": [0.8, 0.2, 4.1, 50.2, 76.4, 93.7],
    "nunca_asistio": [31.0, 0.7, 0.5, 1.2, 1.2, 1.5]
}

# Máximo Nivel Educativo Alcanzado (Población de 25 años y más) - Censo 2022
NIVEL_ALCANZADO_COMPARATIVA = {
    "niveles": [
        "Universitario / Posgrado\nCompleto",
        "Universitario / Superior\nIncompleto",
        "Superior No Univ.\nCompleto",
        "Secundario\nCompleto",
        "Secundario\nIncompleto",
        "Primario\nCompleto",
        "Sin Instrucción / Prim.\nIncompleto"
    ],
    "tres_de_febrero": [16.8, 14.2, 8.5, 27.6, 16.4, 13.2, 3.3],
    "gran_buenos_aires": [10.4, 11.8, 6.2, 24.1, 24.8, 18.6, 4.1],
    "provincia_bs_as": [11.2, 12.1, 6.8, 24.5, 23.7, 17.9, 3.8]
}

# Indicadores TIC / Brecha Digital en el Hogar (Censo 2022 INDEC)
TIC_HOGARES = {
    "indicadores": [
        "Teléfono Celular\ncon Internet",
        "Internet Fija de\nBanda Ancha",
        "Computadora, Notebook\no Tablet"
    ],
    "tres_de_febrero": [94.5, 86.8, 68.4],
    "gran_buenos_aires": [91.8, 79.4, 57.2]
}

# Distribución territorial de Jardines Municipales por Zona / Corredor
JARDINES_POR_ZONA = {
    "zonas": [
        "Corredor Sur\n(Ciudadela, Sáenz Peña, Raffo)",
        "Corredor Centro\n(Caseros, Santos Lugares)",
        "Corredor Noroeste\n(Villa Bosch, Coronado, C. Jardín)",
        "Corredor Norte\n(Podestá, Churruca, Loma Hermosa)"
    ],
    "cantidad_jardines": [6, 8, 5, 8],
    "modalidad_jornada_completa": [2, 3, 1, 4]
}

def generar_grafico_asistencia():
    """Gráfico de barras agrupadas: Asistencia por edad en 3F"""
    fig, ax = plt.subplots(figsize=(10, 5.5), dpi=300)
    x = np.arange(len(ASISTENCIA_POR_EDAD["edades"]))
    width = 0.26

    rects1 = ax.bar(x - width, ASISTENCIA_POR_EDAD["asiste"], width, label='Asiste Actualmente (%)', color='#163C68')
    rects2 = ax.bar(x, ASISTENCIA_POR_EDAD["asistio_pasado"], width, label='Asistió en el Pasado (%)', color='#3B93F7')
    rects3 = ax.bar(x + width, ASISTENCIA_POR_EDAD["nunca_asistio"], width, label='Nunca Asistió (%)', color='#F69321')

    ax.set_ylabel('Porcentaje sobre Total de la Franja Etaria (%)', fontsize=11, fontweight='bold', color='#1E293B')
    ax.set_title('Gráfico 1: Condición de Asistencia Escolar según Grupo de Edad en Tres de Febrero (Censo 2022)', fontsize=13, fontweight='bold', color='#0E2A49', pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels(ASISTENCIA_POR_EDAD["edades"], fontsize=10, fontweight='600')
    ax.legend(frameon=True, facecolor='#F8FAFC', edgecolor='#CBD5E1', fontsize=10)
    ax.grid(axis='y', linestyle='--', alpha=0.5, color='#94A3B8')
    ax.set_ylim(0, 112)

    # Añadir valores sobre barras
    for rect in rects1:
        h = rect.get_height()
        if h > 5:
            ax.annotate(f'{h}%', xy=(rect.get_x() + rect.get_width()/2, h), xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=8.5, fontweight='bold', color='#1E293B')
    for rect in rects3:
        h = rect.get_height()
        if h > 8:
            ax.annotate(f'{h}%', xy=(rect.get_x() + rect.get_width()/2, h), xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=8.5, fontweight='bold', color='#DB7A0B')

    plt.tight_layout()
    out_path = os.path.join(SALIDAS_DIR, 'grafico_asistencia_por_edad_3f.png')
    plt.savefig(out_path)
    plt.close()
    print(f" -> Generado: {out_path}")

def generar_grafico_nivel_alcanzado():
    """Gráfico comparativo horizontal: Máximo nivel educativo en 3F vs GBA"""
    fig, ax = plt.subplots(figsize=(11, 6), dpi=300)
    y = np.arange(len(NIVEL_ALCANZADO_COMPARATIVA["niveles"]))
    height = 0.35

    rects1 = ax.barh(y - height/2, NIVEL_ALCANZADO_COMPARATIVA["tres_de_febrero"], height, label='Tres de Febrero (Censo 2022)', color='#163C68')
    rects2 = ax.barh(y + height/2, NIVEL_ALCANZADO_COMPARATIVA["gran_buenos_aires"], height, label='Promedio 24 Partidos GBA', color='#F69321')

    ax.set_xlabel('Porcentaje de Población de 25 años y más (%)', fontsize=11, fontweight='bold', color='#1E293B')
    ax.set_title('Gráfico 2: Máximo Nivel Educativo Alcanzado en Adultos (Tres de Febrero vs. Conurbano GBA)', fontsize=13, fontweight='bold', color='#0E2A49', pad=15)
    ax.set_yticks(y)
    ax.set_yticklabels(NIVEL_ALCANZADO_COMPARATIVA["niveles"], fontsize=10, fontweight='600')
    ax.invert_yaxis()  # El nivel más alto arriba
    ax.legend(frameon=True, facecolor='#F8FAFC', edgecolor='#CBD5E1', fontsize=10.5, loc='lower right')
    ax.grid(axis='x', linestyle='--', alpha=0.5, color='#94A3B8')
    ax.set_xlim(0, 34)

    for rect in rects1:
        w = rect.get_width()
        ax.annotate(f'{w}%', xy=(w, rect.get_y() + rect.get_height()/2), xytext=(5, 0), textcoords="offset points", ha='left', va='center', fontsize=9.5, fontweight='bold', color='#163C68')
    for rect in rects2:
        w = rect.get_width()
        ax.annotate(f'{w}%', xy=(w, rect.get_y() + rect.get_height()/2), xytext=(5, 0), textcoords="offset points", ha='left', va='center', fontsize=9.5, fontweight='bold', color='#DB7A0B')

    plt.tight_layout()
    out_path = os.path.join(SALIDAS_DIR, 'grafico_nivel_educativo_3f_vs_gba.png')
    plt.savefig(out_path)
    plt.close()
    print(f" -> Generado: {out_path}")

def generar_grafico_tic():
    """Gráfico de Brecha Digital e Indicadores TIC domiciliarios"""
    fig, ax = plt.subplots(figsize=(9.5, 5), dpi=300)
    x = np.arange(len(TIC_HOGARES["indicadores"]))
    width = 0.35

    rects1 = ax.bar(x - width/2, TIC_HOGARES["tres_de_febrero"], width, label='Tres de Febrero (%)', color='#163C68')
    rects2 = ax.bar(x + width/2, TIC_HOGARES["gran_buenos_aires"], width, label='Promedio GBA (%)', color='#B8D0EB')

    ax.set_ylabel('Porcentaje de Hogares Particulares (%)', fontsize=11, fontweight='bold', color='#1E293B')
    ax.set_title('Gráfico 3: Conectividad y Acceso a Tecnologías TIC en los Hogares (Censo 2022 INDEC)', fontsize=13, fontweight='bold', color='#0E2A49', pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels(TIC_HOGARES["indicadores"], fontsize=10.5, fontweight='600')
    ax.legend(frameon=True, facecolor='#F8FAFC', edgecolor='#CBD5E1', fontsize=10.5)
    ax.grid(axis='y', linestyle='--', alpha=0.5, color='#94A3B8')
    ax.set_ylim(0, 110)

    for rect in rects1:
        h = rect.get_height()
        ax.annotate(f'{h}%', xy=(rect.get_x() + rect.get_width()/2, h), xytext=(0, 4), textcoords="offset points", ha='center', va='bottom', fontsize=10, fontweight='bold', color='#163C68')
    for rect in rects2:
        h = rect.get_height()
        ax.annotate(f'{h}%', xy=(rect.get_x() + rect.get_width()/2, h), xytext=(0, 4), textcoords="offset points", ha='center', va='bottom', fontsize=9.5, fontweight='bold', color='#475569')

    plt.tight_layout()
    out_path = os.path.join(SALIDAS_DIR, 'grafico_brecha_digital_tic_3f.png')
    plt.savefig(out_path)
    plt.close()
    print(f" -> Generado: {out_path}")

def generar_grafico_jardines():
    """Gráfico de barras apiladas: Distribución de Jardines Municipales por Corredor"""
    fig, ax = plt.subplots(figsize=(10, 5), dpi=300)
    x = np.arange(len(JARDINES_POR_ZONA["zonas"]))
    width = 0.45

    totales = np.array(JARDINES_POR_ZONA["cantidad_jardines"])
    jornada_comp = np.array(JARDINES_POR_ZONA["modalidad_jornada_completa"])
    jornada_simp = totales - jornada_comp

    rects1 = ax.bar(x, jornada_comp, width, label='Jornada Completa con Almuerzo', color='#F69321')
    rects2 = ax.bar(x, jornada_simp, width, bottom=jornada_comp, label='Jornada Simple (Mañana / Tarde)', color='#163C68')

    ax.set_ylabel('Cantidad de Jardines de Infantes y Maternales', fontsize=11, fontweight='bold', color='#1E293B')
    ax.set_title('Gráfico 4: Red de 27 Jardines Municipales por Corredor y Modalidad (Primera Infancia 3F)', fontsize=13, fontweight='bold', color='#0E2A49', pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels(JARDINES_POR_ZONA["zonas"], fontsize=10, fontweight='600')
    ax.legend(frameon=True, facecolor='#F8FAFC', edgecolor='#CBD5E1', fontsize=10.5)
    ax.grid(axis='y', linestyle='--', alpha=0.5, color='#94A3B8')
    ax.set_ylim(0, 11)

    for i in range(len(x)):
        tot = totales[i]
        jc = jornada_comp[i]
        ax.annotate(f'Total: {tot}\n({jc} J. Completa)', xy=(x[i], tot), xytext=(0, 5), textcoords="offset points", ha='center', va='bottom', fontsize=9.5, fontweight='bold', color='#0E2A49')

    plt.tight_layout()
    out_path = os.path.join(SALIDAS_DIR, 'grafico_distribucion_jardines_localidades.png')
    plt.savefig(out_path)
    plt.close()
    print(f" -> Generado: {out_path}")

if __name__ == "__main__":
    print("--- INICIANDO PROCESAMIENTO Y RENDERING DE GRÁFICOS DE EDUCACIÓN ---")
    generar_grafico_asistencia()
    generar_grafico_nivel_alcanzado()
    generar_grafico_tic()
    generar_grafico_jardines()
    print("[ÉXITO PROCESAMIENTO ESTADÍSTICO DE EDUCACIÓN COMPLETADO EXCLUSIVAMENTE]")
