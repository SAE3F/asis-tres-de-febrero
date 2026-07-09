import os
import sys
import zipfile
import xml.etree.ElementTree as ET

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

def extract_docx_content(docx_path):
    if not os.path.exists(docx_path):
        print(f"Error: No se encontró el archivo {docx_path}")
        return
    
    output_lines = []
    output_lines.append(f"--- CONTENIDO DE: {os.path.basename(docx_path)} ---\n")
    with zipfile.ZipFile(docx_path, 'r') as z:
        xml_content = z.read('word/document.xml')
        tree = ET.fromstring(xml_content)
        
        # XML namespaces en DOCX
        ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
        
        # Recorrer hijos directos del body para mantener orden correcto de párrafos y tablas
        body = tree.find('.//w:body', ns)
        if body is None:
            # Fallback
            body = tree
            
        for child in body:
            if child.tag.endswith('p'):  # Párrafo
                texts = [node.text for node in child.iter() if node.tag.endswith('t') and node.text]
                p_text = ''.join(texts).strip()
                if p_text:
                    output_lines.append(p_text)
            elif child.tag.endswith('tbl'): # Tabla
                output_lines.append("\n[TABLA DETECTADA]")
                for row in child.iter():
                    if row.tag.endswith('tr'):
                        row_texts = []
                        for cell in row.iter():
                            if cell.tag.endswith('tc'):
                                cell_t = ''.join([t.text for t in cell.iter() if t.tag.endswith('t') and t.text]).strip()
                                row_texts.append(cell_t)
                        if row_texts:
                            output_lines.append(" | ".join(row_texts))
                output_lines.append("[FIN TABLA]\n")
                
    output_txt = r"c:\Users\MatiasGiardina\Desktop\salud tres de febrero\boceto_extraido.txt"
    with open(output_txt, "w", encoding="utf-8") as f:
        f.write("\n".join(output_lines))
    print(f"Contenido extraído exitosamente en: {output_txt}")

if __name__ == '__main__':
    docx_file = r"c:\Users\MatiasGiardina\Desktop\salud tres de febrero\Municipalidad de Tres de Febrero - Secretaría de Salud (1).docx"
    extract_docx_content(docx_file)
