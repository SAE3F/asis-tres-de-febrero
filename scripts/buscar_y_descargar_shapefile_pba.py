import os
import sys
import json
import urllib.request
import urllib.error
import geopandas as gpd

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

def probar_descarga_cartografia():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    datos_dir = os.path.join(base_dir, 'datos')
    out_geojson = os.path.join(datos_dir, 'radios_censales_3f_morfologia_real.geojson')
    
    # Lista de URLs de cartografía censal argentina/bonaerense
    urls_candidatas = [
        ("CensAr CABA/AMBA Radios", "https://raw.githubusercontent.com/gonzalo-t/radios_censales_caba_amba/master/data/radios_censales_amba.geojson"),
        ("Datos.gob.ar Radios Censales Nacionales", "https://infra.datos.gob.ar/catalog/modernizacion/dataset/7/distribution/7.24/download/radios-censales.geojson"),
        ("Datos.gob.ar Radios 2010", "https://infra.datos.gob.ar/catalog/modernizacion/dataset/7/distribution/7.22/download/radios-censales-2010.shp.zip"),
        ("IGN GeoServer WFS Capa Censal INDEC", "https://wms.ign.gob.ar/geoserver/sigign/wfs?service=WFS&version=1.0.0&request=GetFeature&typeName=sigign:indec_radio_censal&outputFormat=application/json"),
        ("INDEC GeoServer WFS", "https://geoservicios.indec.gob.ar/geoserver/sig/wfs?service=WFS&version=1.0.0&request=GetFeature&typeName=sig:radios_censales_2022&outputFormat=application/json&cql_filter=provincia='06'%20AND%20departamento='06840'")
    ]
    
    for nombre, url in urls_candidatas:
        print(f"\nProbando conexión y descarga de: {nombre}...")
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=15) as resp:
                print(f" -> [STATUS {resp.status}] Conexión exitosa a {nombre}. Leyendo datos...")
                if url.endswith('.zip'):
                    # Guardar zip temporal y leer con geopandas
                    temp_zip = os.path.join(datos_dir, 'temp_radios.zip')
                    with open(temp_zip, 'wb') as f_zip:
                        f_zip.write(resp.read())
                    gdf = gpd.read_file(f"zip://{temp_zip}")
                    print(" -> Leídas", len(gdf), "geometrías de shapefile en zip.")
                    os.remove(temp_zip)
                else:
                    data_json = json.loads(resp.read().decode('utf-8'))
                    features = data_json.get('features', [])
                    print(f" -> Leídas {len(features)} geometrías en GeoJSON.")
                    gdf = gpd.GeoDataFrame.from_features(features)
                
                # Filtrar específicamente Tres de Febrero (06840 / 840)
                # Inspeccionar columnas
                cols = [c.lower() for c in gdf.columns]
                print(" -> Columnas disponibles:", list(gdf.columns)[:10])
                
                # Buscar columna de link / codprov / partido
                mask = gdf.apply(lambda row: any('06840' in str(v) or 'tres de febrero' in str(v).lower() for v in row.values), axis=1)
                gdf_3f = gdf[mask]
                
                if len(gdf_3f) > 30:
                    print(f"[¡ÉXITO TOTAL!] Filtrados {len(gdf_3f)} polígonos reales de radios censales de Tres de Febrero!")
                    gdf_3f.to_file(out_geojson, driver="GeoJSON", encoding="utf-8")
                    return True
                else:
                    print(f" -> No se encontraron suficientes geometrías para 06840 en {nombre} ({len(gdf_3f)} encontrados).")
        except Exception as e:
            print(f" -> Error con {nombre}: {e}")
            
    print("\n[Nota] Si los endpoints remotos masivos están lentos o bloqueados, generaremos cartografía de polígonos irregulares orgánicos (tipo manzanas y polígonos de Thiessen georreferenciados) que se ajustan al límite exacto de Tres de Febrero y sus calles.")
    return False

if __name__ == '__main__':
    probar_descarga_cartografia()
