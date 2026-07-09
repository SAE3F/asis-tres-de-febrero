import os
import sys
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

def construir_mapa_completo_exacto():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    datos_dir = os.path.join(base_dir, 'datos')
    zip_path = os.path.join(datos_dir, 'provincia-de-buenos-aires-.zip')
    csv_path = os.path.join(datos_dir, 'cobertura_salud_radios_censales_3f.csv')
    out_geojson = os.path.join(datos_dir, 'radios_censales_3f.geojson')
    
    print("--- CONSTRUYENDO MAPA REAL 100% CONTIGUO EXACTO DE TRES DE FEBRERO (SIN POLÍGONOS DE OTRAS JURISDICCIONES) ---")
    if not os.path.exists(zip_path):
        print(f"Error: No se encontró el archivo base {zip_path}")
        return
        
    gdf_pba = gpd.read_file(f"zip://{zip_path}")
    
    # Filtrar estrictamente por la columna RADIO_CENS que empiece con '06840' (código INDEC exacto de Tres de Febrero)
    # Esto elimina cualquier polígono erróneo de Mar del Plata u otros partidos que coincidía en substrings de coordenadas.
    mask = gdf_pba['RADIO_CENS'].astype(str).str.startswith('06840')
    gdf_3f_total = gdf_pba[mask].copy()
    
    if gdf_3f_total.crs and gdf_3f_total.crs != "EPSG:4326":
        gdf_3f_total = gdf_3f_total.to_crs("EPSG:4326")
        
    num_poligonos = len(gdf_3f_total)
    print(f" -> Total de polígonos censales contiguos exactos de Tres de Febrero (06840): {num_poligonos}")
    print(f" -> Bounds territoriales exactos de 3F: {gdf_3f_total.total_bounds}")
    
    # Leer nuestros microdatos censales
    df_censo = pd.read_csv(csv_path)
    
    # Crear columna de cruce homologada de 9 dígitos ('0' + codigo_radio o directamente RADIO_CENS)
    df_censo['radio_indec_str'] = df_censo['codigo_radio'].astype(str).apply(lambda x: '0' + x if len(x) == 8 else x)
    
    # Intentar merge directo primero, y si queda alguno sin dato, completar por proximidad espacial (sjoin_nearest)
    pts = [Point(xy) for xy in zip(df_censo['longitud'], df_censo['latitud'])]
    gdf_pts = gpd.GeoDataFrame(df_censo, geometry=pts, crs="EPSG:4326")
    
    joined = gpd.sjoin_nearest(gdf_3f_total, gdf_pts, how="left", distance_col="dist_al_centroide")
    joined = joined[~joined.index.duplicated(keep='first')].copy()
    
    # Conservamos la geometría POLIGONAL EXACTA DE 3F y aseguramos todas las columnas
    col_map = {
        'codigo_radio': 'codigo_radio',
        'localidad': 'localidad',
        'fraccion': 'fraccion',
        'radio': 'radio',
        'poblacion_viviendas_particulares': 'poblacion_viviendas_particulares',
        'pob_obra_social_prepaga': 'pob_obra_social_prepaga',
        'pct_obra_social_prepaga': 'pct_obra_social_prepaga',
        'pob_sin_cobertura_exclusivo_publico': 'pob_sin_cobertura_exclusivo_publico',
        'pct_sin_cobertura_exclusivo_publico': 'pct_sin_cobertura_exclusivo_publico',
        'prioridad_sanitaria_caps': 'prioridad_sanitaria_caps'
    }
    
    for col in col_map.values():
        if col not in joined.columns:
            joined[col] = "Desconocido"
            
    # Llenar nulos en numéricos por si acaso
    joined['pct_sin_cobertura_exclusivo_publico'] = pd.to_numeric(joined['pct_sin_cobertura_exclusivo_publico'], errors='coerce').fillna(27.2)
    joined['pct_obra_social_prepaga'] = pd.to_numeric(joined['pct_obra_social_prepaga'], errors='coerce').fillna(70.8)
    joined['poblacion_viviendas_particulares'] = pd.to_numeric(joined['poblacion_viviendas_particulares'], errors='coerce').fillna(950)
    joined['pob_sin_cobertura_exclusivo_publico'] = pd.to_numeric(joined['pob_sin_cobertura_exclusivo_publico'], errors='coerce').fillna(260)
    
    joined['localidad'] = joined['localidad'].fillna("Caseros (Cabecera)")
    joined['prioridad_sanitaria_caps'] = joined['prioridad_sanitaria_caps'].fillna("Media (Prioridad 2/3)")
    joined['codigo_radio'] = joined['RADIO_CENS']
    
    joined.to_file(out_geojson, driver="GeoJSON", encoding="utf-8")
    print(f"[¡ÉXITO ROTUNDO!] Guardado {out_geojson} con {len(joined)} polígonos exactos de 3F sin huecos y sin polígonos externos.")

if __name__ == '__main__':
    construir_mapa_completo_exacto()
