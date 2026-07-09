import os
import sys
import urllib.request
import json

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

def check_url(url, description):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            print(f"[OK] {description}: Status {response.status}")
            return True
    except Exception as e:
        print(f"[FALLO] {description}: {e}")
        return False

print("Probando conectividad a fuentes de datos cartográficos y censales de Argentina...")

# IGN API WFS para radios censales o departamentos
ign_url = "https://wms.ign.gob.ar/geoserver/ows?service=WFS&version=1.0.0&request=GetCapabilities"
check_url(ign_url, "IGN Geoserver WFS")

# GitHub repos conocidos con shapefiles/geojson de AMBA / radios censales
github_geojson = "https://raw.githubusercontent.com/martinszulc/radios-censales-amba/master/data/radios_censales_amba.geojson"
check_url(github_geojson, "GitHub Radios Censales AMBA (Martin Szulc)")

github_geo2 = "https://raw.githubusercontent.com/pdelboca/caba-censal/master/data/radios_censales.geojson"
check_url(github_geo2, "GitHub Radios Censales CABA/AMBA")

# IGN capa departamentos buenos aires json
ign_deptos = "https://wms.ign.gob.ar/geoserver/sigign/wfs?service=WFS&version=1.0.0&request=GetFeature&typeName=sigign:departamento&outputFormat=application/json&cql_filter=provincia='Buenos Aires'"
check_url(ign_deptos, "IGN WFS Departamentos Buenos Aires")
