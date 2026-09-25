import json
import zipfile
import xml.etree.ElementTree as ET
import sys
import os
from urllib.parse import quote

def validate_aasx(path):
    print(f"Validating {path}...")
    with zipfile.ZipFile(path, 'r') as z:
        if 'aasx/data.xml' in z.namelist():
            data = z.read('aasx/data.xml')
            root = ET.fromstring(data)
            # Find all AASs and Submodels
            ns = {'aas': 'https://admin-shell.io/aas/3/0'}
            
            submodels = {}
            for sm in root.findall('.//aas:submodels/aas:submodel', ns):
                sm_id = sm.find('aas:id', ns).text
                sm_idshort = sm.find('aas:idShort', ns).text
                submodels[sm_id] = sm_idshort
                
            print(f"  Found {len(submodels)} Submodels:")
            for sm_id, sm_idshort in submodels.items():
                print(f"    - ID: {sm_id} (idShort: {sm_idshort})")
                print(f"      Encoded BaSyx identifier: {quote(sm_id, safe='')}")
                
            aas_list = root.findall('.//aas:assetAdministrationShells/aas:assetAdministrationShell', ns)
            print(f"  Found {len(aas_list)} AASs:")
            for aas in aas_list:
                aas_id = aas.find('aas:id', ns).text
                aas_idshort = aas.find('aas:idShort', ns).text
                print(f"    - ID: {aas_id} (idShort: {aas_idshort})")
                
                # Check submodel references
                refs = aas.findall('.//aas:submodels/aas:reference', ns)
                for ref in refs:
                    keys = ref.findall('aas:keys/aas:key', ns)
                    for key in keys:
                        if key.find('aas:type', ns).text == 'Submodel':
                            ref_id = key.find('aas:value', ns).text
                            resolved = "YES" if ref_id in submodels else "NO"
                            print(f"      Submodel reference: {ref_id}")
                            print(f"      Resolved Submodel: {resolved}")
                            if resolved == "NO":
                                print("      *** MISMATCH ***")
        elif 'aasx/aasenv-with-no-id/aasenv-with-no-id.json' in z.namelist():
            data = z.read('aasx/aasenv-with-no-id/aasenv-with-no-id.json')
            env = json.loads(data)
            submodels = {sm['id']: sm.get('idShort', '') for sm in env.get('submodels', [])}
            print(f"  Found {len(submodels)} Submodels:")
            for sm_id, sm_idshort in submodels.items():
                print(f"    - ID: {sm_id} (idShort: {sm_idshort})")
                print(f"      Encoded BaSyx identifier: {quote(sm_id, safe='')}")
                
            for aas in env.get('assetAdministrationShells', []):
                print(f"    - AAS ID: {aas.get('id')} (idShort: {aas.get('idShort')})")
                for ref in aas.get('submodels', []):
                    for key in ref.get('keys', []):
                        if key.get('type') == 'Submodel':
                            ref_id = key.get('value')
                            resolved = "YES" if ref_id in submodels else "NO"
                            print(f"      Submodel reference: {ref_id}")
                            print(f"      Resolved Submodel: {resolved}")
                            if resolved == "NO":
                                print("      *** MISMATCH ***")
        else:
            print("  Cannot find aasx/data.xml or aasx/aasenv-with-no-id/aasenv-with-no-id.json")
            print("  Namlist: ", z.namelist())
    print("-" * 40)

if __name__ == '__main__':
    template_path = 'model/template/epd-type-iii-submodel-template.aasx'
    instance_path = 'examples/wago-00001/wago-00001-v01-01-en-epd-submodel-instance.aasx'
    
    validate_aasx(template_path)
    validate_aasx(instance_path)
