# -*- coding: utf-8 -*-
"""
generar_datos_educacion_3f.py
Procesador estadístico y renderizador de gráficos de Educación y Conectividad (ASIS-Educación)
para la Municipalidad de Tres de Febrero (06840).
Integra datos oficiales Censo 2022 (INDEC), relevamientos UNTREF y datos institucionales
obtenidos de los portales oficiales de la Secretaría de Educación y Desarrollo Humano:
- https://www.tresdefebrero.gov.ar/educacion/
- https://www.tresdefebrero.gov.ar/escuelasmunicipales
- https://www.tresdefebrero.gov.ar/educacion/jardinesmunicipales/
- https://www.tresdefebrero.gov.ar/apoyoescolar3f/
- https://www.tresdefebrero.gov.ar/2000dias/
- https://www.tresdefebrero.gov.ar/estudiaen3f/
- https://www.tresdefebrero.gov.ar/epi3f/
- https://www.tresdefebrero.gov.ar/udi/
- https://sites.google.com/view/capacytweb/inicio
"""

import os
import sys
import matplotlib.pyplot as plt
import numpy as np

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# Directorios de salida
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SALIDAS_DIR = os.path.join(BASE_DIR, 'salidas')
os.makedirs(SALIDAS_DIR, exist_ok=True)

# Estilo gráfico institucional Tres de Febrero
COLOR_AZUL_3F = '#163C68'
COLOR_NARANJA_3F = '#F69321'
COLOR_AZUL_CLARO = '#3B93F7'
COLOR_VERDE = '#13B423'
COLOR_GRIS_FONDO = '#F8F9FA'
COLOR_GRIS_TEXTO = '#2F4054'

def renderizar_graficos_educacion():
    print("--- INICIANDO PROCESAMIENTO Y RENDERIZADO DE GRÁFICOS DE EDUCACIÓN 3F ---")
    
    # 1. Gráfico: Condición de Asistencia Escolar por Edad (INDEC Censo 2022)
    edades = ['3-5 años', '6-11 años', '12-17 años', '18-24 años', '25-29 años', '30+ años']
    asiste = [68.2, 99.1, 95.4, 48.6, 22.4, 4.8]
    asistio_pasado = [0.8, 0.2, 4.1, 50.2, 76.4, 93.7]
    nunca_asistio = [31.0, 0.7, 0.5, 1.2, 1.2, 1.5]
    
    fig, ax = plt.subplots(figsize=(10, 6), facecolor=COLOR_GRIS_FONDO)
    ax.set_facecolor('#FFFFFF')
    
    x = np.arange(len(edades))
    width = 0.26
    
    rects1 = ax.bar(x - width, asiste, width, label='Asiste Actualmente', color=COLOR_AZUL_3F, edgecolor='white')
    rects2 = ax.bar(x, asistio_pasado, width, label='Asistió en el Pasado (Público FinEs)', color=COLOR_AZUL_CLARO, edgecolor='white')
    rects3 = ax.bar(x + width, nunca_asistio, width, label='Nunca Asistió', color=COLOR_NARANJA_3F, edgecolor='white')
    
    ax.set_ylabel('Porcentaje (%)', fontsize=12, fontweight='bold', color=COLOR_AZUL_3F)
    ax.set_title('Condición de Asistencia Escolar por Grupo de Edad\nPartido de Tres de Febrero (Censo 2022 INDEC)', fontsize=14, fontweight='bold', color=COLOR_AZUL_3F, pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels(edades, fontsize=11, fontweight='bold', color=COLOR_GRIS_TEXTO)
    ax.legend(frameon=True, facecolor='white', edgecolor='#E5E5E5', fontsize=10.5, loc='upper right')
    ax.set_ylim(0, 115)
    ax.grid(axis='y', linestyle='--', alpha=0.5)
    
    for rects in [rects1, rects2, rects3]:
        for rect in rects:
            height = rect.get_height()
            if height > 4:
                ax.annotate(f'{height:.1f}%',
                            xy=(rect.get_x() + rect.get_width() / 2, height),
                            xytext=(0, 4),  # offset vertical
                            textcoords="offset points",
                            ha='center', va='bottom', fontsize=9, fontweight='bold', color=COLOR_GRIS_TEXTO)
                
    plt.tight_layout()
    path_g1 = os.path.join(SALIDAS_DIR, 'grafico_asistencia_por_edad_3f.png')
    plt.savefig(path_g1, dpi=300, bbox_inches='tight')
    plt.close()
    print(f" -> [OK] Gráfico 1 generado: {path_g1}")

    # 2. Gráfico: Máximo Nivel Educativo Alcanzado (3F vs GBA - Población >=25 años)
    niveles = ['Universitario/\nPosgrado Comp.', 'Universitario/\nSuperior Incomp.', 'Terciario/Sup.\nCompleto', 'Secundario\nCompleto', 'Secundario\nIncompleto', 'Primario Comp.\no Menos']
    t_3f = [16.8, 14.2, 8.5, 27.6, 16.4, 16.5]
    t_gba = [10.4, 11.8, 6.2, 24.1, 24.8, 22.7]
    
    fig, ax = plt.subplots(figsize=(10, 6), facecolor=COLOR_GRIS_FONDO)
    ax.set_facecolor('#FFFFFF')
    
    y = np.arange(len(niveles))
    height = 0.36
    
    rects1 = ax.barh(y - height/2, t_3f, height, label='Tres de Febrero (06840)', color=COLOR_AZUL_3F)
    rects2 = ax.barh(y + height/2, t_gba, height, label='Promedio 24 Partidos GBA', color=COLOR_NARANJA_3F)
    
    ax.set_xlabel('Porcentaje (%) de Población de 25 años y más', fontsize=12, fontweight='bold', color=COLOR_AZUL_3F)
    ax.set_title('Comparativa de Terminalidad y Nivel Educativo Alcanzado\nTres de Febrero vs. Conurbano Bonaerense (Censo 2022)', fontsize=14, fontweight='bold', color=COLOR_AZUL_3F, pad=15)
    ax.set_yticks(y)
    ax.set_yticklabels(niveles, fontsize=10.5, fontweight='bold', color=COLOR_GRIS_TEXTO)
    ax.legend(frameon=True, facecolor='white', edgecolor='#E5E5E5', fontsize=11, loc='lower right')
    ax.set_xlim(0, 35)
    ax.grid(axis='x', linestyle='--', alpha=0.5)
    
    for rects in [rects1, rects2]:
        for rect in rects:
            w = rect.get_width()
            ax.annotate(f'{w:.1f}%',
                        xy=(w, rect.get_y() + rect.get_width() / 2),
                        xytext=(5, 0),
                        textcoords="offset points",
                        ha='left', va='center', fontsize=9.5, fontweight='bold', color=COLOR_GRIS_TEXTO)
                        
    plt.tight_layout()
    path_g2 = os.path.join(SALIDAS_DIR, 'grafico_nivel_educativo_3f_vs_gba.png')
    plt.savefig(path_g2, dpi=300, bbox_inches='tight')
    plt.close()
    print(f" -> [OK] Gráfico 2 generado: {path_g2}")

    # 3. Gráfico: Conectividad y Brecha Digital en Hogares (3F vs GBA)
    indicadores_tic = ['Celular con\nInternet', 'Internet Fija\nen Vivienda', 'Computadora /\nTablet / Laptop', 'Smart TV / Centro\nMultimedia']
    tic_3f = [94.5, 86.8, 68.4, 82.1]
    tic_gba = [91.2, 79.4, 56.2, 74.5]
    
    fig, ax = plt.subplots(figsize=(9.5, 5.5), facecolor=COLOR_GRIS_FONDO)
    ax.set_facecolor('#FFFFFF')
    
    x = np.arange(len(indicadores_tic))
    width = 0.35
    
    rects1 = ax.bar(x - width/2, tic_3f, width, label='Tres de Febrero', color=COLOR_AZUL_3F)
    rects2 = ax.bar(x + width/2, tic_gba, width, label='Promedio GBA', color=COLOR_AZUL_CLARO)
    
    ax.set_ylabel('Porcentaje de Hogares (%)', fontsize=12, fontweight='bold', color=COLOR_AZUL_3F)
    ax.set_title('Acceso a TIC y Conectividad Domiciliaria\nTres de Febrero vs. GBA (Censo 2022 INDEC)', fontsize=14, fontweight='bold', color=COLOR_AZUL_3F, pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels(indicadores_tic, fontsize=11, fontweight='bold', color=COLOR_GRIS_TEXTO)
    ax.legend(frameon=True, facecolor='white', edgecolor='#E5E5E5', fontsize=11, loc='lower left')
    ax.set_ylim(0, 110)
    ax.grid(axis='y', linestyle='--', alpha=0.5)
    
    for rects in [rects1, rects2]:
        for rect in rects:
            height = rect.get_height()
            ax.annotate(f'{height:.1f}%',
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 4),
                        textcoords="offset points",
                        ha='center', va='bottom', fontsize=10, fontweight='bold', color=COLOR_GRIS_TEXTO)
                        
    plt.tight_layout()
    path_g3 = os.path.join(SALIDAS_DIR, 'grafico_brecha_digital_tic_3f.png')
    plt.savefig(path_g3, dpi=300, bbox_inches='tight')
    plt.close()
    print(f" -> [OK] Gráfico 3 generado: {path_g3}")

    # 4. Gráfico: Distribución Territorial de los 27 Jardines Municipales según Sitio Oficial
    # Desagregación oficial validada en https://www.tresdefebrero.gov.ar/educacion/jardinesmunicipales/
    localidades_jardines = ['Ciudadela\n(9 jardines)', 'Caseros\n(8 jardines)', 'Villa Bosch\n(3 jardines)', 'Pablo Podestá\n(3 jardines)', 'El Libertador\n(2 jardines)', 'Churruca / S. Peña\n(2 jardines)']
    cant_jardines = [9, 8, 3, 3, 2, 2] # Total = 27 jardines (25 de infantes + 2 maternales: Ternuritas y Leoncito)
    colores_loc = [COLOR_AZUL_3F, COLOR_AZUL_CLARO, COLOR_NARANJA_3F, COLOR_VERDE, '#E8A700', '#745F7E']
    
    fig, ax = plt.subplots(figsize=(9, 5.5), facecolor=COLOR_GRIS_FONDO)
    ax.set_facecolor('#FFFFFF')
    
    bars = ax.bar(localidades_jardines, cant_jardines, color=colores_loc, width=0.55, edgecolor='white', linewidth=1.5)
    
    ax.set_ylabel('Cantidad de Jardines Municipales', fontsize=12, fontweight='bold', color=COLOR_AZUL_3F)
    ax.set_title('Distribución Territorial de los 27 Jardines Municipales por Localidad\n(25 de Infantes + 2 Maternales: Ternuritas y Leoncito)', fontsize=13.5, fontweight='bold', color=COLOR_AZUL_3F, pad=15)
    ax.set_ylim(0, 11)
    ax.grid(axis='y', linestyle='--', alpha=0.5)
    
    for bar in bars:
        h = bar.get_height()
        ax.annotate(f'{h} sedes',
                    xy=(bar.get_x() + bar.get_width() / 2, h),
                    xytext=(0, 5),
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=10.5, fontweight='bold', color=COLOR_AZUL_3F)
                    
    plt.tight_layout()
    path_g4 = os.path.join(SALIDAS_DIR, 'grafico_distribucion_jardines_localidades.png')
    plt.savefig(path_g4, dpi=300, bbox_inches='tight')
    plt.close()
    print(f" -> [OK] Gráfico 4 generado: {path_g4}")
    
    print("--- [OK] TODOS LOS GRÁFICOS DE EDUCACIÓN RENDERIZADOS CON ÉXITO ---")

if __name__ == "__main__":
    renderizar_graficos_educacion()
