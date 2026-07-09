import os
import sys
import json
import urllib.request
import urllib.parse

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

def buscar_en_ckan():
    queries = ["radios censales", "06840", "tres de febrero censo", "cartografia censal", "radios censales 2022"]
    
    for q in queries:
        url = f"https://datos.gob.ar/api/3/action/package_search?q={urllib.parse.quote(q)}"
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=12) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                results = data.get('result', {}).get('results', [])
                if results:
                    print(f"\n[QUERY: '{q}'] -> Encontrados {len(results)} datasets:")
                    for r in results[:4]:
                        title = r.get('title')
                        print(f"  * Dataset: {title}")
                        for res in r.get('resources', []):
                            fmt = res.get('format', '').upper()
                            res_url = res.get('url')
                            if fmt in ['SHP', 'GEOJSON', 'SHAPEFILE', 'KML', 'ZIP', 'JSON']:
                                print(f"     -> Recurso [{fmt}]: {res_url}")
        except Exception as e:
            print(f"Error consultando '{q}': {e}")

if __name__ == '__main__':
    buscar_en_ckan()
