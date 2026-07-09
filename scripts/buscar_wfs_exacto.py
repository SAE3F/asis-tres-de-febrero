import os
import sys
import urllib.request
import xml.etree.ElementTree as ET

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

url = "https://wms.ign.gob.ar/geoserver/ows?service=WFS&version=1.0.0&request=GetCapabilities"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, timeout=20) as resp:
    xml_data = resp.read()

tree = ET.fromstring(xml_data)
ns = {'wfs': 'http://www.opengis.net/wfs', 'ows': 'http://www.opengis.net/ows'}

print("Buscando capas en GetCapabilities...")
for ft in tree.findall('.//{http://www.opengis.net/wfs}FeatureType') + tree.findall('.//FeatureType'):
    name_node = ft.find('{http://www.opengis.net/wfs}Name')
    if name_node is None:
        name_node = ft.find('Name')
    if name_node is not None and name_node.text:
        t = name_node.text.lower()
        if any(k in t for k in ['cens', 'radio', 'fracc', 'partido', 'depto', 'municip', 'amba', 'pba']):
            title_node = ft.find('{http://www.opengis.net/wfs}Title') or ft.find('Title')
            title = title_node.text if title_node is not None else ""
            print(f" -> Capa WFS disponible: {name_node.text} | Título: {title}")
