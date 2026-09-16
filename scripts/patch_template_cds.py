import os
import zipfile
import xml.etree.ElementTree as ET
import yaml
import io

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_AASX = os.path.join(REPO_ROOT, "model", "template", "epd-type-iii-submodel-template.aasx")
REGISTRY_YAML = os.path.join(REPO_ROOT, "docs", "model", "environmental-indicator-registry.yaml")

NS_URI = "https://admin-shell.io/aas/3/0"
ET.register_namespace("aas", NS_URI)

def T(local: str) -> str:
    return "{" + NS_URI + "}" + local

def add_cd(cd_root, id_val, id_short, pref_name, def_text, dt="STRING"):
    cd = ET.SubElement(cd_root, T("conceptDescription"))
    ET.SubElement(cd, T("id")).text = id_val
    ET.SubElement(cd, T("idShort")).text = id_short
    # administration
    admin = ET.SubElement(cd, T("administration"))
    ET.SubElement(admin, T("version")).text = "1"
    ET.SubElement(admin, T("revision")).text = "0"
    
    # embeddedDataSpecifications
    eds = ET.SubElement(cd, T("embeddedDataSpecifications"))
    eds_el = ET.SubElement(eds, T("embeddedDataSpecification"))
    
    ds = ET.SubElement(eds_el, T("dataSpecification"))
    ET.SubElement(ds, T("type")).text = "ExternalReference"
    keys = ET.SubElement(ds, T("keys"))
    k = ET.SubElement(keys, T("key"))
    ET.SubElement(k, T("type")).text = "GlobalReference"
    ET.SubElement(k, T("value")).text = "https://admin-shell.io/DataSpecificationTemplates/DataSpecificationIEC61360/3/0"
    
    ds_content = ET.SubElement(eds_el, T("dataSpecificationContent"))
    iec = ET.SubElement(ds_content, T("dataSpecificationIec61360"))
    
    pn = ET.SubElement(iec, T("preferredName"))
    lst = ET.SubElement(pn, T("langStringPreferredNameTypeIec61360"))
    ET.SubElement(lst, T("language")).text = "en"
    ET.SubElement(lst, T("text")).text = pref_name
    
    df = ET.SubElement(iec, T("definition"))
    lst2 = ET.SubElement(df, T("langStringDefinitionTypeIec61360"))
    ET.SubElement(lst2, T("language")).text = "en"
    ET.SubElement(lst2, T("text")).text = def_text
    
    ET.SubElement(iec, T("dataType")).text = dt
    
    return iec

def add_value_list(cd_root, iec, values, is_open=False, prefix_url="https://wg-epd.example.com/draft/v1/Value/"):
    # values: list of tuples (value, desc)
    vl = ET.SubElement(iec, T("valueList"))
    v_refs = ET.SubElement(vl, T("valueReferencePairs"))
    for v, d in values:
        vr = ET.SubElement(v_refs, T("valueReferencePair"))
        ET.SubElement(vr, T("value")).text = v
        
        val_id = f"{prefix_url}{v.replace(' ', '_')}"
        vid = ET.SubElement(vr, T("valueId"))
        ET.SubElement(vid, T("type")).text = "ExternalReference"
        k = ET.SubElement(vid, T("keys"))
        k1 = ET.SubElement(k, T("key"))
        ET.SubElement(k1, T("type")).text = "GlobalReference"
        ET.SubElement(k1, T("value")).text = val_id
        
        # Auto-generate a CD for this vocabulary value if it's our own namespace to prevent dangling
        if prefix_url.startswith("https://wg-epd.example.com"):
            add_cd(cd_root, id_val=val_id, id_short=v.replace(' ', '_'), pref_name=v, def_text=d or f"Vocabulary value: {v}")

def patch_template():
    with zipfile.ZipFile(TEMPLATE_AASX, "r") as z:
        names = z.namelist()
        files = {n: z.read(n) for n in names}
        
    data_xml_bytes = files.get("aasx/data.xml")
    tree = ET.parse(io.BytesIO(data_xml_bytes))
    root = tree.getroot()
    
    cd_root = root.find(T("conceptDescriptions"))
    if cd_root is None:
        cd_root = ET.SubElement(root, T("conceptDescriptions"))
        
    # 1. Remove obsolete LCIA and IDTA ConceptDescriptions
    for cd_el in list(cd_root):
        id_el = cd_el.find(T("id"))
        if id_el is not None and id_el.text and "admin-shell.io/idta/EPD" in id_el.text:
            cd_root.remove(cd_el)
            
    # Load registry for indicator codes
    with open(REGISTRY_YAML, 'r', encoding='utf-8') as f:
        registry = yaml.safe_load(f)
        
    indicator_values = [(ind['indicatorCode'], ind.get('indicatorName', '')) for ind in registry['indicators']]
    
    # Generate explicit ConceptDescription for each indicator to prevent dangling references
    for ind in registry['indicators']:
        ind_code = ind['indicatorCode']
        ind_name = ind.get('indicatorName', ind_code)
        def_text = f"Indicator: {ind_name}. Characterization Unit: {ind.get('characterizationUnit', '')}."
        if ind.get('baseUnit'):
            def_text += f" Base Unit: {ind.get('baseUnit')}."
            
        add_cd(cd_root, 
               id_val=f"https://wg-epd.example.com/draft/v1/Indicator/{ind_code}",
               id_short=ind_code,
               pref_name=ind_name,
               def_text=def_text,
               dt="REAL_MEASURE")

    # Add modern CDs
    iec_ic = add_cd(cd_root, "https://wg-epd.example.com/draft/v1/IndicatorCode", "indicatorCode", "Indicator Code", 
           "Code identifying the environmental impact, resource-use, waste or output-flow indicator represented by this EnvironmentalResult. Use a recognised vocabulary value where applicable; additional indicators may be introduced where required by the applicable PCR or EPD programme and must be semantically identified.")
    add_value_list(cd_root, iec_ic, indicator_values, prefix_url="https://wg-epd.example.com/draft/v1/Indicator/")
    
    iec_sc = add_cd(cd_root, "https://wg-epd.example.com/draft/v1/StageCode", "stageCode", "Lifecycle Stage Code", 
           "Code identifying the lifecycle stage. The ValueList defines the recognised standard vocabulary supported by this Submodel version. Additional values may be used where required.")
    stages = [("A1", ""), ("A2", ""), ("A3", ""), ("A1-A3", ""), ("A4", ""), ("A5", ""), ("B1", ""), ("B2", ""), ("B3", ""), ("B4", ""), ("B5", ""), ("B6", ""), ("B7", ""), ("C1", ""), ("C2", ""), ("C3", ""), ("C4", ""), ("D", "")]
    add_value_list(cd_root, iec_sc, stages)
    
    iec_rc = add_cd(cd_root, "https://wg-epd.example.com/draft/v1/ResultCategory", "resultCategory", "Result Category",
           "Category of the environmental result (Closed vocabulary).")
    cats = [("ImpactIndicator", ""), ("ResourceUse", ""), ("Waste", ""), ("OutputFlow", "")]
    add_value_list(cd_root, iec_rc, cats)
    
    iec_ss = add_cd(cd_root, "https://wg-epd.example.com/draft/v1/StageStatus", "stageStatus", "Stage Status",
           "Status of the declaration for this stage (Closed vocabulary).")
    statuses = [("Assessed", ""), ("NotAssessed", "")]
    add_value_list(cd_root, iec_ss, statuses)

    iec_vs = add_cd(cd_root, "https://wg-epd.example.com/draft/v1/ValueStatus", "valueStatus", "Value Status",
           "Status of the numeric value (Closed vocabulary).")
    v_statuses = [("Declared", ""), ("NotDeclared", "")]
    add_value_list(cd_root, iec_vs, v_statuses)

    iec_sit = add_cd(cd_root, "https://wg-epd.example.com/draft/v1/ManufacturingSite/Type", "siteType", "Site Type",
            "Type of the manufacturing site (Closed vocabulary).")
    add_value_list(cd_root, iec_sit, [("Fixed", ""), ("Mobile", "")])
    
    iec_sct = add_cd(cd_root, "https://wg-epd.example.com/draft/v1/EPDScope/Type", "scopeType", "Scope Type",
            "Type of the EPD scope (Closed vocabulary).")
    add_value_list(cd_root, iec_sct, [("Instance", ""), ("Class", "")])
    
    add_cd(cd_root, "https://wg-epd.example.com/draft/v1/Unit", "unit", "Unit", "Characterization unit of the result.")
    add_cd(cd_root, "https://wg-epd.example.com/draft/v1/UnitId", "unitId", "Unit ID", "Semantic ID of the characterization unit.")
    add_cd(cd_root, "https://wg-epd.example.com/draft/v1/BaseUnit", "baseUnit", "Base Unit", "The underlying physical/reference unit component.")
    add_cd(cd_root, "https://wg-epd.example.com/draft/v1/BaseUnitId", "baseUnitId", "Base Unit ID", "Semantic ID of the underlying physical unit.")

    ET.indent(tree, space="  ")
    buf = io.BytesIO()
    tree.write(buf, encoding="utf-8", xml_declaration=True)
    patched_xml = buf.getvalue()
    
    tmp_path = TEMPLATE_AASX + ".tmp"
    with zipfile.ZipFile(tmp_path, "w", compression=zipfile.ZIP_DEFLATED) as zout:
        for name, data in files.items():
            if name == "aasx/data.xml":
                zout.writestr(name, patched_xml)
            else:
                zout.writestr(name, data)
                
    os.replace(tmp_path, TEMPLATE_AASX)
    print("Template patched.")

if __name__ == "__main__":
    patch_template()
