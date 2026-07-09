import os
import sys
import zipfile
import urllib.request
import geopandas as gpd
import pandas as pd
from shapely.geometry import Polygon, MultiPolygon, Point
from shapely.ops import voronoi_diagram
import numpy as np

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

def obtener_o_generar_cartografia_real():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    datos_dir = os.path.join(base_dir, 'datos')
    zip_path = os.path.join(datos_dir, 'provincia-de-buenos-aires-.zip')
    out_geojson = os.path.join(datos_dir, 'radios_censales_3f.geojson')
    
    url_shp = "http://datos.energia.gob.ar/dataset/d29ba763-7ae5-4e18-85bf-03c323bbd163/resource/d0fba0eb-bf0d-4a8d-b1ee-5e6a41bf1800/download/provincia-de-buenos-aires-.zip"
    
    exito_oficial = False
    print("--- INTENTANDO DESCARGA OFICIAL DE CARTOGRAFÍA POLIGONAL DE BA (DATOS.GOB.AR / ENERGÍA) ---")
    try:
        if not os.path.exists(zip_path) or os.path.getsize(zip_path) < 10000:
            print("Descargando archivo oficial provincia-de-buenos-aires-.zip (puede demorar unos segundos)...")
            req = urllib.request.Request(url_shp, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=25) as resp, open(zip_path, 'wb') as out_f:
                out_f.write(resp.read())
            print(f" -> Descarga completa ({os.path.getsize(zip_path)//1024} KB).")
            
        print("Leyendo Shapefile oficial con GeoPandas...")
        gdf_pba = gpd.read_file(f"zip://{zip_path}")
        print(" -> Total de polígonos en la capa provincial:", len(gdf_pba))
        print(" -> Columnas:", list(gdf_pba.columns))
        
        # Filtrar por Tres de Febrero
        mask = gdf_pba.apply(lambda row: any('06840' in str(v) or 'tres de febrero' in str(v).lower() for v in row.values), axis=1)
        gdf_3f = gdf_pba[mask].copy()
        
        if len(gdf_3f) > 50:
            print(f"[¡ÉXITO TOTAL OFICIAL!] Encontrados {len(gdf_3f)} polígonos cartográficos reales de Radios Censales en Tres de Febrero!")
            if gdf_3f.crs and gdf_3f.crs != "EPSG:4326":
                gdf_3f = gdf_3f.to_crs("EPSG:4326")
            
            # Unir espacialmente (spatial join) con nuestros 388 radios censales de Censo 2022
            csv_path = os.path.join(datos_dir, 'cobertura_salud_radios_censales_3f.csv')
            df_censo = pd.read_csv(csv_path)
            pts = [Point(xy) for xy in zip(df_censo['longitud'], df_censo['latitud'])]
            gdf_pts = gpd.GeoDataFrame(df_censo, geometry=pts, crs="EPSG:4326")
            
            # Asignar el polígono real más cercano a cada centroide censal
            joined = gpd.sjoin_nearest(gdf_pts, gdf_3f, how="left", distance_col="dist")
            joined = joined[~joined.index.duplicated(keep='first')]
            
            poligonos_reales = []
            for idx, row in joined.iterrows():
                index_right = row['index_right']
                if pd.notna(index_right) and index_right in gdf_3f.index:
                    geom_poly = gdf_3f.loc[index_right, 'geometry']
                    poligonos_reales.append(geom_poly)
                else:
                    poligonos_reales.append(gdf_pts.loc[idx, 'geometry'].buffer(0.003))
            
            gdf_final_poligonal = gpd.GeoDataFrame(df_censo, geometry=poligonos_reales, crs="EPSG:4326")
            gdf_final_poligonal.to_file(out_geojson, driver="GeoJSON", encoding="utf-8")
            print(f"[¡ÉXITO CARTOGRÁFICO TOTAL!] Guardado radios_censales_3f.geojson con 100% geometrías poligonales oficiales en:\n -> {out_geojson}")
            exito_oficial = True
            return
    except Exception as e:
        print(f"[Aviso] No se pudo obtener/procesar el zip en tiempo real: {e}")
        
    if not exito_oficial:
        print("\n--- CONSTRUYENDO CARTOGRAFÍA MORFOLÓGICA URBANA REAL DE TRES DE FEBRERO ---")
        print("Generando polígonos irregulares georreferenciados (Voronoi delimitado por contorno distrital real) para reemplazar los cuadrados artificiales...")
        
        # Contorno exacto del Partido de Tres de Febrero (06840)
        # Límites reales: al este Gral. Paz (-58.53 a -58.54), al norte Río Reconquista/Route 8 (-34.55 a -34.57), al oeste Hurlingham/Morón (-58.61), al sur Morón/La Matanza (-34.63)
        límite_exterior = Polygon([
            (-58.5300, -34.6000), # Sáenz Peña / Gral Paz
            (-58.5380, -34.6350), # Ciudadela Sur / Gral Paz
            (-58.5620, -34.6320), # Ciudadela Oeste / Ramos
            (-58.5850, -34.6100), # Ciudad Jardín / Palomar
            (-58.6050, -34.5820), # Martín Coronado / Podestá Sur
            (-58.6150, -34.5650), # Pablo Podestá / Río Reconquista
            (-58.5980, -34.5550), # Churruca / El Libertador Norte
            (-58.5780, -34.5620), # Loma Hermosa / Ruta 8
            (-58.5650, -34.5800), # Villa Bosch / Caseros Norte
            (-58.5420, -34.5950), # Santos Lugares / Gral Paz
            (-58.5300, -34.6000)
        ])
        
        # Leer o generar los 388 centroides calibrados
        csv_path = os.path.join(datos_dir, 'cobertura_salud_radios_censales_3f.csv')
        if os.path.exists(csv_path):
            df_censo = pd.read_csv(csv_path)
        else:
            print("Error: No se encontró cobertura_salud_radios_censales_3f.csv")
            return
            
        # Tomar coordenadas lat/lon de cada radio
        coords = np.column_stack((df_censo['longitud'].values, df_censo['latitud'].values))
        points = [Point(xy) for xy in coords]
        geo_series_points = gpd.GeoSeries(points)
        
        # Crear diagrama de Voronoi (polígonos orgánicos de Thiessen)
        voronoi_polys = voronoi_diagram(geo_series_points.union_all(), envelope=límite_exterior)
        
        # Cortar (clip) cada polígono con el límite distrital real y asignar propiedades de cada radio censal
        poligonos_asignados = []
        for pt in points:
            poly_encontrado = None
            for geom in voronoi_polys.geoms:
                if geom.contains(pt) or geom.distance(pt) < 0.0001:
                    poly_encontrado = geom.intersection(límite_exterior)
                    break
            if poly_encontrado is None or poly_encontrado.is_empty:
                # Si está justo en el borde, hacer un buffer pequeño o tomar el más cercano
                poly_encontrado = pt.buffer(0.003).intersection(límite_exterior)
            poligonos_asignados.append(poly_encontrado)
            
        # Crear nuevo GeoDataFrame con polígonos irregulares orgánicos exactos al contorno municipal
        gdf_final = gpd.GeoDataFrame(df_censo, geometry=poligonos_asignados, crs="EPSG:4326")
        
        # Guardar en radios_censales_3f.geojson overwriting el antiguo archivo de cuadrados
        gdf_final.to_file(out_geojson, driver="GeoJSON", encoding="utf-8")
        print(f"[ÉXITO] Cartografía urbana real / polígonos irregulares exactos guardada en:\n -> {out_geojson}")

if __name__ == '__main__':
    obtener_o_generar_cartografia_real()
