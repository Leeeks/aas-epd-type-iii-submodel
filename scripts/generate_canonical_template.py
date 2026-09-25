import xml.etree.ElementTree as ET
import zipfile
import io
import os
import shutil

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_AASX = os.path.join(REPO_ROOT, "model", "template", "epd-type-iii-submodel-template.aasx")
NS_URI = "https://admin-shell.io/aas/3/0"
NS = {"aas": NS_URI}

def T(local: str) -> str:
    return "{" + NS_URI + "}" + local

def find_by_id(container: ET.Element, id_short: str):
    if container is None: return None
    for child in container:
        id_el = child.find(T("idShort"))
        if id_el is not None and id_el.text == id_short:
            return child
    return None

def clear_value(el: ET.Element):
    if el is None: return
    val = el.find(T("value"))
    if val is not None:
        val.text = ""
        
def clear_multi_lang(el: ET.Element):
    if el is None: return
    for text_el in el.findall(".//" + T("langStringTextType") + "/" + T("text")):
        text_el.text = ""

def clean_template():
    print(f"Cleaning template: {TEMPLATE_AASX}")
    with zipfile.ZipFile(TEMPLATE_AASX, "r") as z:
        names = z.namelist()
        files = {n: z.read(n) for n in names}
        
    data_xml_bytes = files.get("aasx/data.xml")
    tree = ET.parse(io.BytesIO(data_xml_bytes))
    root = tree.getroot()
    
    # 1. Update Asset Information
    asset_info = root.find(".//" + T("assetInformation"))
    if asset_info is not None:
        asset_kind = asset_info.find(T("assetKind"))
        if asset_kind is None:
            asset_kind = ET.SubElement(asset_info, T("assetKind"))
        asset_kind.text = "Type"  # Templates apply to a Type, not Instance. Or we can use "NotApplicable"
        
        global_asset_id = asset_info.find(T("globalAssetId"))
        if global_asset_id is not None:
            global_asset_id.text = ""
            
    # 2. AAS ID
    aas = root.find(".//" + T("assetAdministrationShell"))
    aas_id = aas.find(T("id"))
    TEMPLATE_AAS_ID = "https://admin-shell.io/idta/EPD/EPDTypeIII/Template/1/0/AAS"
    TEMPLATE_SM_ID = "https://admin-shell.io/idta/EPD/EPDTypeIII/Template/1/0"
    if aas_id is not None:
        aas_id.text = TEMPLATE_AAS_ID
        
    # AAS ref to Submodel
    ref_val = aas.find(".//" + T("submodels") + "//" + T("reference") + "//" + T("key") + "//" + T("value"))
    if ref_val is not None:
        ref_val.text = TEMPLATE_SM_ID

    # 3. Submodel ID & Kind
    sm = root.find(".//" + T("submodel"))
    sm_id_el = sm.find(T("id"))
    if sm_id_el is not None:
        sm_id_el.text = TEMPLATE_SM_ID
        
    kind_el = sm.find(T("kind"))
    if kind_el is None:
        kind_el = ET.Element(T("kind"))
        # insert kind after idShort (or just append)
        sm.insert(1, kind_el)
    kind_el.text = "Template"
    
    # 4. Strip concrete values
    sme = sm.find(T("submodelElements"))
    
    # identificationPublication
    ip = find_by_id(sme, "identificationPublication")
    if ip is not None:
        v = ip.find(T("value"))
        clear_value(find_by_id(v, "documentIdentifier"))
        
    # manufacturerProduct
    mp = find_by_id(sme, "manufacturerProduct")
    if mp is not None:
        v = mp.find(T("value"))
        if v is not None:
            clear_multi_lang(find_by_id(v, "manufacturerName"))
            clear_multi_lang(find_by_id(v, "productName"))
            clear_value(find_by_id(v, "productArticleNumberOfManufacturer"))
            clear_multi_lang(find_by_id(v, "manufacturingDescription"))
        
            # manufacturingSites
            ms = find_by_id(v, "manufacturingSites")
            if ms is not None:
                ms_v = ms.find(T("value"))
                if ms_v is not None:
                    # Clear all elements in the list because template should have empty list
                    for child in list(ms_v):
                        ms_v.remove(child)

    # epdScope
    epd_scope = find_by_id(sme, "EPDScope")
    if epd_scope is not None:
        v = epd_scope.find(T("value"))
        if v is not None:
            clear_multi_lang(find_by_id(v, "scopeDescription"))
        
    # files
    for file_el in sme.findall(".//" + T("file")):
        clear_value(file_el)
        
    # coveredProductReferences
    cpr = find_by_id(find_by_id(sme, "manufacturerProduct").find(T("value")) if find_by_id(sme, "manufacturerProduct") is not None else None, "coveredProductReferences")
    if cpr is not None:
        v = cpr.find(T("value"))
        if v is not None:
            # Clear all elements in the list
            for child in list(v):
                v.remove(child)

    # 5. Remove any SubmodelElementList idShorts which are invalid in BaSyx (except the list itself, its children shouldn't have idShort)
    for lst in root.findall(".//" + T("submodelElementList")):
        v = lst.find(T("value"))
        if v is not None:
            for child in v:
                c_id = child.find(T("idShort"))
                if c_id is not None:
                    child.remove(c_id)

    # 6. Serialise
    ET.indent(tree, space="  ")
    buf = io.BytesIO()
    tree.write(buf, encoding="utf-8", xml_declaration=True)
    patched_xml = buf.getvalue()
    
    # 7. Write back out, omitting instance files
    tmp_path = TEMPLATE_AASX + ".tmp"
    with zipfile.ZipFile(tmp_path, "w", compression=zipfile.ZIP_DEFLATED) as zout:
        for name, data in files.items():
            if name == "aasx/data.xml":
                zout.writestr(name, patched_xml)
            elif name.endswith(".jpg") or name.endswith(".pdf"):
                print(f"Omitting instance file: {name}")
                continue
            else:
                zout.writestr(name, data)
                
    os.replace(tmp_path, TEMPLATE_AASX)
    print("Template generation complete!")

if __name__ == "__main__":
    clean_template()
