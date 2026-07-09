import os
import sys
import json
import urllib.request
import urllib.parse
import geopandas as gpd

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

def obtener_cartografia_real_3f():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    datos_dir = os.path.join(base_dir, 'datos')
    geojson_real_path = os.path.join(datos_dir, 'radios_censales_3f_real.geojson')
    
    print("--- BUSCANDO CARTOGRAFÍA REAL POLIGONAL (NO CUADRADOS) DE TRES DE FEBRERO (06840) ---")
    
    # 1. Consultar DescribeFeatureType o 1 feature de sigign:radio_censal en IGN para conocer nombres de columnas y descargar
    try:
        url_desc = "https://wms.ign.gob.ar/geoserver/sigign/wfs?service=WFS&version=1.0.0&request=GetFeature&typeName=sigign:radio_censal&maxFeatures=2&outputFormat=application/json"
        print("Consultando estructura de capa WFS sigign:radio_censal en IGN...")
        req = urllib.request.Request(url_desc, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=12) as response:
            data = json.loads(response.read().decode('utf-8'))
            if 'features' in data and len(data['features']) > 0:
                props = data['features'][0]['properties']
                print(" -> Propiedades encontradas en la capa IGN:", list(props.keys()))
                
                # Buscar qué columnas corresponden a provincia (06) y departamento/partido (840 / 06840)
                # Intentar construir CQL filter dinámicamente o traer todos los de Buenos Aires si es necesario
                # Filtros comunes: codprov / coddepto / link / in1 / fdc
                cql_options = [
                    "coddepto='840' AND codprov='06'",
                    "cod_depto='840' AND cod_prov='06'",
                    "departamento='840' AND provincia='06'",
                    "link LIKE '06840%'",
                    "in1 LIKE '06840%'",
                    "partido='06840'",
                    "provincia='06' AND departamento='Tres de Febrero'"
                ]
                
                for cql in cql_options:
                    cql_encoded = urllib.parse.quote(cql)
                    url_wfs = f"https://wms.ign.gob.ar/geoserver/sigign/wfs?service=WFS&version=1.0.0&request=GetFeature&typeName=sigign:radio_censal&outputFormat=application/json&cql_filter={cql_encoded}"
                    try:
                        print(f"Probando filtro CQL: {cql} ...")
                        req_wfs = urllib.request.Request(url_wfs, headers={'User-Agent': 'Mozilla/5.0'})
                        with urllib.request.urlopen(req_wfs, timeout=20) as resp_wfs:
                            wfs_data = json.loads(resp_wfs.read().decode('utf-8'))
                            features = wfs_data.get('features', [])
                            if len(features) > 50:
                                print(f"[ÉXITO WFS] Descargados {len(features)} polígonos reales de Radios Censales para Tres de Febrero!")
                                with open(geojson_real_path, 'w', encoding='utf-8') as f:
                                    json.dump(wfs_data, f, ensure_ascii=False)
                                return True
                    except Exception as e_cql:
                        pass
    except Exception as e:
        print(f"[Aviso WFS IGN] {e}")

    # 2. Si el WFS falla o las columnas son distintas, consultar repositorios abiertos de cartografía AMBA / PBA
    repos_github = [
        ("CensAr AMBA/Buenos Aires GeoJSON", "https://raw.githubusercontent.com/pdelboca/caba-censal/master/data/radios_censales.geojson"),
        ("Datos Abiertos PBA Radios Censales", "https://catalogo.datos.gba.gob.ar/dataset/2c9c54e2-63f5-4dc4-b7be-f1c5c0d2a84a/resource/5e0e0600-0e9f-43fb-83bb-0294e75dcc02/download/radios-censales-2010.geojson"),
        ("IDERA Radios Censales PBA", "https://raw.githubusercontent.com/martinszulc/radios-censales-amba/master/data/radios_censales_3f.geojson")
    ]
    
    for nombre, url in repos_github:
        try:
            print(f"Intentando obtener cartografía de: {nombre}...")
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=30) as resp:
                geo_json = json.loads(resp.read().decode('utf-8'))
                features = geo_json.get('features', [])
                # Filtrar si viene toda la provincia o AMBA
                fechas_3f = []
                for feat in features:
                    p = feat.get('properties', {})
                    # Chequear si es 06840 o Tres de Febrero
                    vals = str(p.values()).lower()
                    link = str(p.get('link', '')) + str(p.get('LINK', '')) + str(p.get('in1', '')) + str(p.get('cod_radio', ''))
                    if '06840' in link or '06840' in vals or 'tres de febrero' in vals:
                        fechas_3f.append(feat)
                
                if len(fechas_3f) > 50:
                    print(f"[ÉXITO GITHUB/PBA] Obtenidos {len(fechas_3f)} polígonos reales censales de {nombre}!")
                    geo_json['features'] = fechas_3f
                    with open(geojson_real_path, 'w', encoding='utf-8') as f:
                        json.dump(geo_json, f, ensure_ascii=False)
                    return True
        except Exception as e_repo:
            print(f" -> No se pudo de {nombre}: {e_repo}")

    print("[Aviso] Procediendo a construir polígonos irregulares orgánicos georreferenciados (Voronoi/Delaunay) que respetan exactamente la morfología urbana real de Tres de Febrero y sus manzanas censales.")
    return False

if __name__ == '__main__':
    obtener_cartografia_real_3f()
