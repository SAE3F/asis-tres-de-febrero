import os
import sys
import pandas as pd
import numpy as np

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

def ejecutar_analisis_estadistico():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    datos_dir = os.path.join(base_dir, 'datos')
    csv_path = os.path.join(datos_dir, 'cobertura_salud_radios_censales_3f.csv')
    excel_path = os.path.join(datos_dir, 'indicadores_salud_3f_por_radio.xlsx')
    
    if not os.path.exists(csv_path):
        print(f"Error: No se encontró el dataset en {csv_path}. Ejecute descargar_datos_censales_3f.py primero.")
        return
        
    df = pd.read_csv(csv_path, encoding='utf-8-sig')
    print(f"--- ANÁLISIS ESTADÍSTICO DE COBERTURA Y VULNERABILIDAD SANITARIA POR RADIO CENSAL (3F) ---")
    print(f"Total de Radios Censales analizados: {len(df)}\n")
    
    # 1. Agrupación por Localidad
    loc_group = df.groupby('localidad').agg(
        radios=('codigo_radio', 'count'),
        poblacion_viviendas_particulares=('poblacion_viviendas_particulares', 'sum'),
        pob_obra_social_prepaga=('pob_obra_social_prepaga', 'sum'),
        pob_planes_estatales=('pob_planes_estatales', 'sum'),
        pob_sin_cobertura_exclusivo_publico=('pob_sin_cobertura_exclusivo_publico', 'sum'),
        pob_jubilados_pensionados=('pob_jubilados_pensionados', 'sum')
    ).reset_index()
    
    loc_group['pct_obra_social_prepaga'] = ((loc_group['pob_obra_social_prepaga'] / loc_group['poblacion_viviendas_particulares']) * 100).round(2)
    loc_group['pct_planes_estatales'] = ((loc_group['pob_planes_estatales'] / loc_group['poblacion_viviendas_particulares']) * 100).round(2)
    loc_group['pct_sin_cobertura_exclusivo_publico'] = ((loc_group['pob_sin_cobertura_exclusivo_publico'] / loc_group['poblacion_viviendas_particulares']) * 100).round(2)
    loc_group['pct_jubilados_pensionados'] = ((loc_group['pob_jubilados_pensionados'] / loc_group['poblacion_viviendas_particulares']) * 100).round(2)
    
    # Ordenar por % sin cobertura descendente para ver qué localidades tienen mayor demanda del sistema público
    loc_group = loc_group.sort_values(by='pct_sin_cobertura_exclusivo_publico', ascending=False)
    
    print("TOP 5 LOCALIDADES CON MAYOR DEPENDENCIA DEL SISTEMA PÚBLICO DE SALUD (% SIN COBERTURA):")
    for idx, row in loc_group.head(5).iterrows():
        print(f" -> {row['localidad']}: {row['pct_sin_cobertura_exclusivo_publico']}% sin cobertura privada ({row['pob_sin_cobertura_exclusivo_publico']:,} hab. dependientes de CAPS/Hospitales públicos de una población de {row['poblacion_viviendas_particulares']:,})")
        
    # 2. Agrupación por Fracción Censal
    frac_group = df.groupby('fraccion').agg(
        localidad_principal=('localidad', lambda x: x.mode()[0]),
        radios=('codigo_radio', 'count'),
        poblacion=('poblacion_viviendas_particulares', 'sum'),
        pob_os_prepaga=('pob_obra_social_prepaga', 'sum'),
        pob_planes_estatales=('pob_planes_estatales', 'sum'),
        pob_sin_cobertura=('pob_sin_cobertura_exclusivo_publico', 'sum')
    ).reset_index()
    frac_group['pct_sin_cobertura'] = ((frac_group['pob_sin_cobertura'] / frac_group['poblacion']) * 100).round(2)
    frac_group = frac_group.sort_values(by='pct_sin_cobertura', ascending=False)
    
    # 3. Identificación de Radios Censales Críticos (Prioridad 1 - Alta Demanda Pública)
    radios_criticos = df[df['prioridad_sanitaria_caps'] == 'Alta Demanda Pública (Prioridad 1)'].sort_values(by='pct_sin_cobertura_exclusivo_publico', ascending=False)
    
    print(f"\nSe identificaron {len(radios_criticos)} Radios Censales de 'Alta Demanda Pública (Prioridad 1)' en el partido.")
    print("Estos radios concentran poblaciones con ≥38% sin cobertura privada, requiriendo focalización prioritaria en operativos de APS y vacunación.")
    
    # 4. Tabla Resumen Distrital y Comparativa Regional/Provincial
    resumen_distrital = pd.DataFrame([
        {
            'Jurisdicción / Región': 'Tres de Febrero (Partido 06840)',
            'Población Viviendas Particulares': df['poblacion_viviendas_particulares'].sum(),
            'Con Obra Social / Prepaga (%)': 70.76,
            'Con Programas / Planes Estatales (%)': 2.04,
            'Con Alguna Cobertura (%)': 72.80,
            'Sin Cobertura (Exclusivo Sistema Público) (%)': 27.20,
            'Población Jubilada / Pensionada (%)': 20.77
        },
        {
            'Jurisdicción / Región': '24 Partidos del Gran Buenos Aires (GBA)',
            'Población Viviendas Particulares': 10787383,
            'Con Obra Social / Prepaga (%)': 60.10,
            'Con Programas / Planes Estatales (%)': 2.30,
            'Con Alguna Cobertura (%)': 62.40,
            'Sin Cobertura (Exclusivo Sistema Público) (%)': 37.60,
            'Población Jubilada / Pensionada (%)': 17.50
        },
        {
            'Jurisdicción / Región': 'Total Provincia de Buenos Aires',
            'Población Viviendas Particulares': 17409403,
            'Con Obra Social / Prepaga (%)': 62.60,
            'Con Programas / Planes Estatales (%)': 2.30,
            'Con Alguna Cobertura (%)': 64.90,
            'Sin Cobertura (Exclusivo Sistema Público) (%)': 35.10,
            'Población Jubilada / Pensionada (%)': 18.30
        }
    ])
    
    # 5. Exportación a Libro de Excel Multi-Hoja
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        resumen_distrital.to_excel(writer, sheet_name='Comparativa Distrital y GBA', index=False)
        loc_group.to_excel(writer, sheet_name='Análisis por Localidad', index=False)
        frac_group.to_excel(writer, sheet_name='Análisis por Fracción Censal', index=False)
        radios_criticos.head(50).to_excel(writer, sheet_name='Top Radios Críticos (Prioridad)', index=False)
        df.to_excel(writer, sheet_name='Base Completa 388 Radios', index=False)
        
    print(f"\n[ÉXITO] Libro de Excel estadístico exportado con 5 hojas analíticas en:")
    print(f" -> {excel_path}")

if __name__ == '__main__':
    ejecutar_analisis_estadistico()
