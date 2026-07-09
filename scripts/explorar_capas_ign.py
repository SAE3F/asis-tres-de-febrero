import sys
import urllib.request
import xml.etree.ElementTree as ET

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

url = "https://wms.ign.gob.ar/geoserver/ows?service=WFS&version=1.0.0&request=GetCapabilities"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, timeout=15) as resp:
    xml_data = resp.read()

tree = ET.fromstring(xml_data)
# Buscar todos los FeatureType
layers = []
for elem in tree.iter():
    if elem.tag.endswith('Name') and elem.text and ('sigign' in elem.text or 'ign' in elem.text or 'cens' in elem.text or 'radio' in elem.text or 'fracc' in elem.text or 'depto' in elem.text or 'prov' in elem.text):
        layers.append(elem.text)

print(f"Capas encontradas de interés ({len(layers)}):")
for l in sorted(set(layers)):
    if any(k in l.lower() for k in ['cens', 'radio', 'fracc', 'depto', 'prov', 'partido', 'municip']):
        print(" ->", l)
