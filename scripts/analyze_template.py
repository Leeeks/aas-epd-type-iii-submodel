import xml.etree.ElementTree as ET
import zipfile

NS_URI = "https://admin-shell.io/aas/3/0"
NS = {"aas": NS_URI}

def T(local: str) -> str:
    return "{" + NS_URI + "}" + local

def analyze_aasx(path: str):
    print(f"\n==============================")
    print(f"ANALYZING: {path}")
    print(f"==============================")
    
    with zipfile.ZipFile(path, "r") as z:
        data = z.read("aasx/data.xml")
    root = ET.fromstring(data)
    
    # Check Asset Information
    asset_info = root.find(".//" + T("assetInformation"))
    if asset_info is not None:
        asset_kind = asset_info.find(T("assetKind"))
        global_asset_id = asset_info.find(T("globalAssetId"))
        print(f"AssetKind: {asset_kind.text if asset_kind is not None else 'None'}")
        print(f"GlobalAssetId: {global_asset_id.text if global_asset_id is not None else 'None'}")
    
    # 1. Check Submodel Kind
    sm_el = root.find(".//" + T("submodel"))
    if sm_el is None:
        print("ERROR: No submodel found")
        return
        
    kind_el = sm_el.find(".//" + T("kind"))
    kind = kind_el.text if kind_el is not None else "NOT DEFINED (default is Instance)"
    print(f"Submodel.kind = {kind}")
    
    # 2. Submodel ID
    id_el = sm_el.find(T("id"))
    sm_id = id_el.text if id_el is not None else "NOT DEFINED"
    print(f"Submodel.id = {sm_id}")
    
    # 3. Check for instance-specific WAGO values
    print("\nConcrete Property values:")
    
    sm_elements = sm_el.find(T("submodelElements"))
    
    properties = sm_elements.findall(".//" + T("property"))
    for prop in properties:
        id_short = prop.find(T("idShort"))
        val = prop.find(T("value"))
        if id_short is not None and val is not None and val.text:
            if "wago" in val.text.lower() or "221" in val.text:
                print(f" - {id_short.text}: {val.text}")
                
    ml_properties = sm_elements.findall(".//" + T("multiLanguageProperty"))
    for prop in ml_properties:
        id_short = prop.find(T("idShort"))
        ls = prop.find(".//" + T("langStringTextType") + "/" + T("text"))
        if id_short is not None and ls is not None and ls.text:
            if "wago" in ls.text.lower() or "221" in ls.text:
                print(f" - {id_short.text}: {ls.text}")
                
    files = sm_elements.findall(".//" + T("file"))
    for prop in files:
        id_short = prop.find(T("idShort"))
        val = prop.find(T("value"))
        if id_short is not None and val is not None and val.text:
            if "wago" in val.text.lower() or "221" in val.text:
                print(f" - {id_short.text} (File): {val.text}")

if __name__ == "__main__":
    analyze_aasx("model/template/epd-type-iii-submodel-template.aasx")
    analyze_aasx("examples/wago-00001/wago-00001-v01-01-en-epd-submodel-instance.aasx")
