import xml.etree.ElementTree as ET
import zipfile
import json
import sys
import os

NS_URI = "https://admin-shell.io/aas/3/0"
NS = {"aas": NS_URI}

def T(local: str) -> str:
    return "{" + NS_URI + "}" + local

def analyze_environmental_results(path: str):
    print(f"\n==============================")
    print(f"ANALYZING: {path}")
    print(f"==============================")
    
    with zipfile.ZipFile(path, "r") as z:
        data = z.read("aasx/data.xml")
    root = ET.fromstring(data)
    
    sm_elements = root.find(".//" + T("submodel") + "/" + T("submodelElements"))
    if sm_elements is None:
        print("ERROR: No submodelElements found")
        return
        
    er_list = None
    for el in sm_elements.findall(".//" + T("submodelElementList")):
        id_el = el.find(T("idShort"))
        if id_el is not None and id_el.text == "EnvironmentalResults":
            er_list = el
            break
            
    if er_list is None:
        print("ERROR: No EnvironmentalResults found")
        return
        
    er_val = er_list.find(T("value"))
    if er_val is None:
        print("EnvironmentalResults has no value element")
        return
        
    children = list(er_val)
    print(f"EnvironmentalResults contains {len(children)} children.")
    
    for i, child in enumerate(children[:3]):
        tag = child.tag.split("}")[-1]
        id_el = child.find(T("idShort"))
        id_text = id_el.text if id_el is not None else "NONE"
        print(f"  Child {i}: <{tag}> idShort={id_text}")
        
        # Look for indicatorCode inside
        c_val = child.find(T("value"))
        if c_val is not None:
            indicator = None
            stage_values = None
            
            print("    Properties:")
            for prop in c_val:
                p_id = prop.find(T("idShort"))
                p_id_str = p_id.text if p_id is not None else "NONE"
                print(f"      - {p_id_str}")
                
                if p_id is not None:
                    if p_id.text == "indicatorCode":
                        v_el = prop.find(T("value"))
                        indicator = v_el.text if v_el is not None else "EMPTY"
                    if p_id.text == "stageValues":
                        stage_values = prop
            
            print(f"    indicatorCode: {indicator}")
            
            if stage_values is not None:
                sv_val = stage_values.find(T("value"))
                sv_children = list(sv_val) if sv_val is not None else []
                print(f"    stageValues: {len(sv_children)} children")
                for j, sv_child in enumerate(sv_children[:2]):
                    sv_tag = sv_child.tag.split("}")[-1]
                    sv_id = sv_child.find(T("idShort"))
                    sv_id_text = sv_id.text if sv_id is not None else "NONE"
                    
                    stage_code = None
                    svc_val = sv_child.find(T("value"))
                    if svc_val is not None:
                        for sprop in svc_val:
                            sp_id = sprop.find(T("idShort"))
                            if sp_id is not None and sp_id.text == "stageCode":
                                svv_el = sprop.find(T("value"))
                                stage_code = svv_el.text if svv_el is not None else "EMPTY"
                                
                    print(f"      SV Child {j}: <{sv_tag}> idShort={sv_id_text} stageCode={stage_code}")
                if len(sv_children) > 2:
                    print(f"      ... and {len(sv_children) - 2} more stageValues")
                    
    if len(children) > 3:
        print(f"  ... and {len(children) - 3} more children")
        
if __name__ == "__main__":
    analyze_environmental_results("model/template/epd-type-iii-submodel-template.aasx")
    analyze_environmental_results("examples/wago-00001/wago-00001-v01-01-en-epd-submodel-instance.aasx")
