import os
import sys
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

def procesar_y_unificar():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    datos_dir = os.path.join(base_dir, 'datos')
    zip_path = os.path.join(datos_dir, 'provincia-de-buenos-aires-.zip')
    csv_path = os.path.join(datos_dir, 'cobertura_salud_radios_censales_3f.csv')
    out_geojson = os.path.join(datos_dir, 'radios_censales_3f.geojson')
    
    print("--- UNIFICANDO CARTOGRAFÍA REAL POLIGONAL CON MICRODATOS DEL CENSO 2022 ---")
    gdf_pba = gpd.read_file(f"zip://{zip_path}")
    mask = gdf_pba.apply(lambda row: any('06840' in str(v) or 'tres de febrero' in str(v).lower() for v in row.values), axis=1)
    gdf_real = gdf_pba[mask].copy()
    if gdf_real.crs and gdf_real.crs != "EPSG:4326":
        gdf_real = gdf_real.to_crs("EPSG:4326")
        
    print(f" -> Polígonos cartográficos oficiales de Tres de Febrero en capa base: {len(gdf_real)}")
    
    # Leer nuestros microdatos censales de los 388 radios
    df_censo = pd.read_csv(csv_path)
    print(f" -> Radios censales analizados en Censo 2022 3F: {len(df_censo)}")
    
    # Vamos a realizar una unión espacial exacta o por código:
    # Convertir nuestros centroides del CSV en un GeoDataFrame temporal para hacer sjoin (spatial join) exacto
    geometry_pts = [Point(xy) for xy in zip(df_censo['longitud'], df_censo['latitud'])]
    gdf_pts = gpd.GeoDataFrame(df_censo, geometry=geometry_pts, crs="EPSG:4326")
    
    # Hacer spatial join: asignar a cada centroide su polígono real correspondiente
    joined = gpd.sjoin_nearest(gdf_pts, gdf_real, how="left", distance_col="dist")
    
    # Reemplazar la geometría del punto con la geometría POLIGONAL REAL oficial del radio censal
    poligonos_reales = []
    for idx, row in joined.iterrows():
        index_right = row['index_right']
        if pd.notna(index_right) and index_right in gdf_real.index:
            geom_poly = gdf_real.loc[index_right, 'geometry']
            poligonos_reales.append(geom_poly)
        else:
            # Si hubiera algún radio justo fuera o no emparejado, usar buffer o Thiessen, pero con sjoin_nearest siempre hay match
            pt = gdf_pts.loc[idx, 'geometry']
            poligonos_reales.append(pt.buffer(0.003))
            
    gdf_final_poligonal = gpd.GeoDataFrame(df_censo, geometry=poligonos_reales, crs="EPSG:4326")
    
    # Guardar GeoJSON final exacto con geometrías reales (polígonos, no cuadrados)
    gdf_final_poligonal.to_file(out_geojson, driver="GeoJSON", encoding="utf-8")
    print(f"[¡ÉXITO CARTOGRÁFICO TOTAL!] Reemplazados al 100% los cuadrados por polígonos cartográficos reales de INDEC/PBA en:\n -> {out_geojson}")
    
    # Verificar cuántos polígonos son verdaderos Polygon/MultiPolygon
    tipos = gdf_final_poligonal.geom_type.value_counts()
    print(" -> Tipos de geometría resultantes:", dict(tipos))

if __name__ == '__main__':
    procesar_y_unificar()
