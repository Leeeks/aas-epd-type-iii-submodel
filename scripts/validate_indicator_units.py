import sys
import os
import zipfile
import xml.etree.ElementTree as ET
import yaml
import io

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGISTRY_YAML = os.path.join(REPO_ROOT, "docs", "model", "environmental-indicator-registry.yaml")

NS_URI = "https://admin-shell.io/aas/3/0"
ET.register_namespace("aas", NS_URI)

def T(local: str) -> str:
    return "{" + NS_URI + "}" + local

def load_registry():
    with open(REGISTRY_YAML, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    return data.get('indicators', [])

def get_prop_val(smc, id_short):
    for child in smc:
        el = child.find(T("idShort"))
        if el is not None and el.text == id_short:
            v = child.find(T("value"))
            return v.text if v is not None else None
    return None

def validate_aasx(aasx_path):
    indicators = load_registry()
    valid_pairs = {(ind['indicatorCode'], ind['characterizationUnit']) for ind in indicators}
    
    with zipfile.ZipFile(aasx_path, 'r') as z:
        data_xml = z.read("aasx/data.xml")
        
    tree = ET.parse(io.BytesIO(data_xml))
    root = tree.getroot()
    
    errors = []
    
    for er_sml in root.iter(T("submodelElementList")):
        ids = er_sml.find(T("idShort"))
        if ids is not None and ids.text == "EnvironmentalResults":
            val = er_sml.find(T("value"))
            if val is not None:
                for smc in val.iter(T("submodelElementCollection")):
                    sid = smc.find(T("idShort"))
                    # Top-level items in EnvironmentalResults
                    smc_val = smc.find(T("value"))
                    if smc_val is None: continue
                    
                    ind_code = get_prop_val(smc_val, "indicatorCode")
                    if ind_code: # means it's an EnvironmentalResult SMC
                        unit = get_prop_val(smc_val, "unit")
                        if (ind_code, unit) not in valid_pairs:
                            errors.append(f"Invalid pair: indicatorCode='{ind_code}', unit='{unit}' is not in the registry.")
                        
                        # Validate baseUnit if present
                        for child in smc_val:
                            if child.find(T("idShort")) is not None and child.find(T("idShort")).text == "baseUnit":
                                bu_val = child.find(T("value"))
                                bu_unit = get_prop_val(bu_val, "unit")
                                bu_id = get_prop_val(bu_val, "unitId")
                                if not bu_unit or not bu_id:
                                    errors.append(f"baseUnit is missing unit or unitId for {ind_code}")
                                    
    if errors:
        print("Validation FAILED:")
        for err in errors:
            print(f"  - {err}")
        return False
    else:
        print("Validation PASSED: All indicatorCode + characterizationUnit combinations are valid.")
        return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: python validate_indicator_units.py <path_to_aasx>")
        sys.exit(1)
    
    aasx_file = sys.argv[1]
    if not os.path.isfile(aasx_file):
        print(f"File not found: {aasx_file}")
        sys.exit(1)
        
    if not validate_aasx(aasx_file):
        sys.exit(1)
