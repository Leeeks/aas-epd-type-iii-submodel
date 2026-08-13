import os
import sys
import zipfile
import xml.etree.ElementTree as ET
import zlib
import base64
import urllib.request
import re

AASX_PATH = os.path.join("model", "template", "epd-type-iii-submodel-template.aasx")
DOCS_MODEL_DIR = os.path.join("docs", "model")
SECTIONS_DIR = os.path.join(DOCS_MODEL_DIR, "sections")

NS = {'aas': 'https://admin-shell.io/aas/3/0'}

def get_text(el, tag, default=None):
    if el is None: return default
    child = el.find(tag, NS)
    return child.text if child is not None else default

class ModelNode:
    def __init__(self, el, parent=None):
        self.el = el
        self.parent = parent
        self.id_short = get_text(el, 'aas:idShort')
        
        # Tag name without namespace
        raw_tag = el.tag.split('}')[-1]
        self.tag_type = raw_tag
        
        self.semantic_id = None
        sem_el = el.find('aas:semanticId/aas:keys/aas:key/aas:value', NS)
        if sem_el is not None:
            self.semantic_id = sem_el.text
            
        self.value_type = get_text(el, 'aas:valueType')
        
        self.cardinality = "0..*" if raw_tag == 'submodelElementList' else "1"
        qualifiers = el.find('aas:qualifiers', NS)
        if qualifiers is not None:
            for q in qualifiers.findall('aas:qualifier', NS):
                t = get_text(q, 'aas:type')
                if t == 'SMT/Cardinality':
                    v = get_text(q, 'aas:value')
                    if v == 'ZeroToOne': self.cardinality = "0..1"
                    elif v == 'One': self.cardinality = "1"
                    elif v == 'ZeroToMany': self.cardinality = "0..*"
                    elif v == 'OneToMany': self.cardinality = "1..*"
                    elif v: self.cardinality = v
                    
        self.children = []
        val_el = el.find('aas:value', NS)
        if val_el is not None and len(list(val_el)) > 0:
            for child in val_el:
                if isinstance(child.tag, str) and child.tag.startswith('{'):
                    self.children.append(ModelNode(child, self))

def get_stereotype(tag_type):
    mapping = {
        'submodelElementCollection': '<<SMC>>',
        'submodelElementList': '<<SML>>',
        'property': '<<Property>>',
        'multiLanguageProperty': '<<MLP>>',
        'file': '<<File>>',
        'referenceElement': '<<ReferenceElement>>',
        'submodel': '<<Submodel>>'
    }
    return mapping.get(tag_type, f'<<{tag_type}>>')

def short_sem_id(sem_id, semantic_map):
    if not sem_id: return None
    if sem_id not in semantic_map:
        idx = len(semantic_map) + 1
        semantic_map[sem_id] = f"Sem_{idx:03d}"
    return semantic_map[sem_id]

def format_node(node, semantic_map):
    stereotype = get_stereotype(node.tag_type)
    lines = [f'class {node.id_short} {stereotype} {{']
    
    # Metadata
    if node.value_type:
        lines.append(f'  valueType: {node.value_type}')
    
    sem_ref = short_sem_id(node.semantic_id, semantic_map)
    if sem_ref:
        lines.append(f'  sem: {sem_ref}')
        
    lines.append('}')
    return "\n".join(lines)

def generate_puml(root_nodes, semantic_map, title="EPD Type III Model", wrap_packages=False):
    lines = [
        "@startuml",
        f"title {title}",
        "skinparam classAttributeIconSize 0",
        "skinparam linetype ortho",
        "hide empty members",
        ""
    ]
    
    def walk_classes(nodes):
        for n in nodes:
            lines.append(format_node(n, semantic_map))
            walk_classes(n.children)
            
    if wrap_packages:
        for n in root_nodes:
            lines.append(f'package "{n.id_short}" {{')
            walk_classes([n])
            lines.append(f'}}')
    else:
        walk_classes(root_nodes)
        
    lines.append("")
    
    def walk_relations(nodes, parent_id_short):
        for n in nodes:
            card = f'"{n.cardinality}"' if n.cardinality else ""
            lines.append(f'{parent_id_short} *-- {card} {n.id_short}')
            walk_relations(n.children, n.id_short)
            
    for n in root_nodes:
        walk_relations(n.children, n.id_short)
        
    lines.append("@enduml")
    return "\n".join(lines)

def plantuml_encode(text):
    z = zlib.compress(text.encode('utf-8'))
    b = z[2:-4]
    b64 = base64.b64encode(b).decode('ascii')
    b64_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
    puml_chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_"
    return b64.translate(str.maketrans(b64_chars, puml_chars))

def render_svg(puml_text, out_path):
    print(f"Rendering SVG for {out_path}...")
    enc = plantuml_encode(puml_text)
    url = "http://www.plantuml.com/plantuml/svg/" + enc
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        response = urllib.request.urlopen(req)
        svg_data = response.read().decode('utf-8')
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(svg_data)
    except Exception as e:
        print(f"Error rendering SVG {out_path}: {e}")

def main():
    if not os.path.exists(SECTIONS_DIR):
        os.makedirs(SECTIONS_DIR)
        
    with zipfile.ZipFile(AASX_PATH, 'r') as z:
        with z.open('aasx/data.xml') as f:
            tree = ET.parse(f)
            
    root = tree.getroot()
    sm_el = root.find('.//aas:submodel', NS)
    if sm_el is None:
        print("Error: No submodel found in data.xml")
        sys.exit(1)
        
    sm_node = ModelNode(sm_el)
    smes_el = sm_el.find('aas:submodelElements', NS)
    if smes_el is not None:
        for child in smes_el:
            if isinstance(child.tag, str) and child.tag.startswith('{'):
                sm_node.children.append(ModelNode(child, sm_node))
                
    semantic_map = {}
    
    # 1. Master diagram
    master_puml = generate_puml(sm_node.children, semantic_map, wrap_packages=True)
    master_puml_path = os.path.join(DOCS_MODEL_DIR, "epd-type-iii-model.puml")
    with open(master_puml_path, 'w', encoding='utf-8') as f:
        f.write(master_puml)
    render_svg(master_puml, os.path.join(DOCS_MODEL_DIR, "epd-type-iii-model.svg"))
    
    # 2. Section diagrams
    for child in sm_node.children:
        section_puml = generate_puml([child], semantic_map, title=child.id_short)
        section_puml_path = os.path.join(SECTIONS_DIR, f"{child.id_short}.puml")
        with open(section_puml_path, 'w', encoding='utf-8') as f:
            f.write(section_puml)
        render_svg(section_puml, os.path.join(SECTIONS_DIR, f"{child.id_short}.svg"))
        
    # 3. Semantic references table
    sem_md_path = os.path.join(DOCS_MODEL_DIR, "semantic-references.md")
    with open(sem_md_path, 'w', encoding='utf-8') as f:
        f.write("# Semantic References\n\n")
        f.write("| Short ID | Full Semantic URI/IRDI |\n")
        f.write("|---|---|\n")
        # Sort by short ID
        for full_id, short_id in sorted(semantic_map.items(), key=lambda x: x[1]):
            f.write(f"| `{short_id}` | `{full_id}` |\n")
            
    # 4. README.md
    readme_path = os.path.join(DOCS_MODEL_DIR, "README.md")
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write("# EPD Type III Submodel UML Documentation\n\n")
        f.write("## Purpose\n")
        f.write("The UML diagrams provide a structural overview of the EPD Type III AAS submodel.\n\n")
        f.write("## Source of Truth\n")
        f.write("> **Note:** The UML source and rendered diagrams are generated from the same model definition used to create the EPD Type III AAS template (`model/template/epd-type-iii-submodel-template.aasx`). Manual changes to generated files will be overwritten.\n\n")
        f.write("## UML Notation\n")
        f.write("- `<<SMC>>`: SubmodelElementCollection\n")
        f.write("- `<<SML>>`: SubmodelElementList\n")
        f.write("- `<<Property>>`: Property\n")
        f.write("- `<<MLP>>`: MultiLanguageProperty\n")
        f.write("- `<<File>>`: File\n\n")
        f.write("## Regeneration\n")
        f.write("To regenerate these diagrams after a model change, run:\n")
        f.write("```bash\npython scripts/generate_model_uml.py\n```\n\n")
        f.write("## Master Diagram\n")
        f.write("![Master Diagram](epd-type-iii-model.svg)\n\n")
        f.write("## Detailed Views\n")
        for child in sm_node.children:
            f.write(f"- [{child.id_short}](sections/{child.id_short}.svg)\n")
        f.write("\n## Semantic References\n")
        f.write("See [semantic-references.md](semantic-references.md) for full URI mappings of the `Sem_XXX` compact IDs used in the diagrams.\n")

if __name__ == "__main__":
    main()
