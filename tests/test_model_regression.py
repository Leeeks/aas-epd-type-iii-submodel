import os
import sys
import zipfile
import xml.etree.ElementTree as ET

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NS_URI = "https://admin-shell.io/aas/3/0"
NS = {"aas": NS_URI}

def T(local: str) -> str:
    return "{" + NS_URI + "}" + local

def find_by_id(container: ET.Element, id_short: str):
    for child in container:
        id_el = child.find(T("idShort"))
        if id_el is not None and id_el.text == id_short:
            return child
    return None

def test_aasx(path: str):
    print(f"\nTesting {os.path.basename(path)}...")
    with zipfile.ZipFile(path, "r") as z:
        data = z.read("aasx/data.xml")
    
    root = ET.fromstring(data)
    
    # Extract all concept descriptions
    cd_ids = set()
    for cd in root.iter(T("conceptDescription")):
        id_el = cd.find(T("id"))
        if id_el is not None and id_el.text:
            cd_ids.add(id_el.text)
            
    # Submodels
    sm_elements = root.find(f".//{T('submodel')}/{T('submodelElements')}")
    assert sm_elements is not None, "submodelElements not found"
    
    # 1. LCAMethodology assertions
    lca = find_by_id(sm_elements, "LCAMethodology")
    assert lca is not None, "LCAMethodology missing"
    lca_val = lca.find(T("value"))
    
    legacy_fields = ["referenceFlow.id", "referenceFlow.amount", "pictogramSource", "flowDiagramSource", "dataSetValidUntil", "technicalPurpose"]
    for child in lca_val:
        id_el = child.find(T("idShort"))
        if id_el is not None:
            assert id_el.text not in legacy_fields, f"Legacy field {id_el.text} found in LCAMethodology!"
            assert id_el.text != "location", "'location' should be 'geographicalScope'"
            assert id_el.text != "referenceYear", "'referenceYear' should be 'lcaReferenceYear'"
            assert id_el.text != "energyModel", "'energyModel' should be 'lcaEnergyModel'"
    print("  PASS LCAMethodology structure")
            
    # 2. ContentDeclaration assertions
    cd = find_by_id(sm_elements, "ContentDeclaration")
    assert cd is not None, "ContentDeclaration missing"
    cd_val = cd.find(T("value"))
    
    # No flat biogenicCarbonContent properties
    for child in cd_val:
        id_el = child.find(T("idShort"))
        if id_el is not None:
            assert id_el.text not in ("biogenicCarbonContentProduct", "biogenicCarbonContentPackaging"), "Flat biogenicCarbon properties found!"
            
    bcc = find_by_id(cd_val, "biogenicCarbonContent")
    assert bcc is not None, "biogenicCarbonContent SMC missing in ContentDeclaration"
    bcc_v = bcc.find(T("value"))
    assert find_by_id(bcc_v, "biogenicCarbonContentProduct") is not None, "biogenicCarbonContentProduct missing"
    assert find_by_id(bcc_v, "biogenicCarbonContentPackaging") is not None, "biogenicCarbonContentPackaging missing"
    
    mp = find_by_id(sm_elements, "manufacturerProduct")
    if mp is not None:
        mp_val = mp.find(T("value"))
        assert find_by_id(mp_val, "biogenicCarbonContent") is None, "biogenicCarbonContent should not be in manufacturerProduct"
    print("  PASS ContentDeclaration structure")
    
    # 3. EPDScope assertions
    scope = find_by_id(sm_elements, "EPDScope")
    if scope is not None:
        s_val = scope.find(T("value"))
        assert find_by_id(s_val, "sourceDeclarationReference") is None, "sourceDeclarationReference found in EPDScope"
    print("  PASS EPDScope structure")
    
    # 4. Semantic Dangling Reference assertions
    # Find all ValueLists and their valueIds
    for v_ref in root.iter(T("valueReferencePair")):
        v_id = v_ref.find(T("valueId"))
        if v_id is not None:
            key_val = v_id.find(f".//{T('key')}/{T('value')}")
            if key_val is not None:
                sem_id = key_val.text
                assert sem_id in cd_ids, f"Dangling semantic reference: {sem_id} is not present as a ConceptDescription!"
    print("  PASS Semantic References (no dangling references)")

    # 5. Identifier Consistency assertions
    # Ensure that every AAS submodel reference matches a Submodel ID in the environment
    sm_actual_ids = set()
    for sm in root.iter(T("submodel")):
        id_el = sm.find(T("id"))
        if id_el is not None and id_el.text:
            sm_actual_ids.add(id_el.text)
            
    aas_refs = set()
    for aas in root.iter(T("assetAdministrationShell")):
        submodels_list = aas.find(T("submodels"))
        if submodels_list is not None:
            for ref in submodels_list.iter(T("reference")):
                key_val = ref.find(f".//{T('keys')}/{T('key')}/{T('value')}")
                if key_val is not None and key_val.text:
                    aas_refs.add(key_val.text)
                    
    for ref_id in aas_refs:
        assert ref_id in sm_actual_ids, f"Dangling AAS Submodel reference: '{ref_id}' not found in package Submodels!"
    print("  PASS Identifier Consistency (no dangling AAS submodel references)")


if __name__ == "__main__":
    template = os.path.join(REPO_ROOT, "model", "template", "epd-type-iii-submodel-template.aasx")
    instance = os.path.join(REPO_ROOT, "examples", "wago-00001", "wago-00001-v01-01-en-epd-submodel-instance.aasx")
    
    if os.path.exists(template):
        test_aasx(template)
    
    if os.path.exists(instance):
        test_aasx(instance)
    
    print("\nAll regression tests passed successfully!")
