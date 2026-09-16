import os
import zipfile
import xml.etree.ElementTree as ET
import yaml
import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_AASX = os.path.join(REPO_ROOT, "model", "template", "epd-type-iii-submodel-template.aasx")
REGISTRY_YAML = os.path.join(REPO_ROOT, "docs", "model", "environmental-indicator-registry.yaml")
INSTANCE_AASX = os.path.join(REPO_ROOT, "examples", "wago-00001", "wago-00001-v01-01-en-epd-submodel-instance.aasx")

NS_URI = "https://admin-shell.io/aas/3/0"
ET.register_namespace("aas", NS_URI)

def T(local: str) -> str:
    return "{" + NS_URI + "}" + local

@pytest.fixture(scope="module")
def template_tree():
    with zipfile.ZipFile(TEMPLATE_AASX, "r") as z:
        data_xml_bytes = z.read("aasx/data.xml")
    return ET.fromstring(data_xml_bytes)

@pytest.fixture(scope="module")
def instance_tree():
    with zipfile.ZipFile(INSTANCE_AASX, "r") as z:
        data_xml_bytes = z.read("aasx/data.xml")
    return ET.fromstring(data_xml_bytes)

def test_registry_validity():
    with open(REGISTRY_YAML, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    assert 'indicators' in data
    assert len(data['indicators']) > 0
    
    for ind in data['indicators']:
        assert 'indicatorCode' in ind
        assert 'characterizationUnit' in ind

def test_template_has_no_legacy_cds(template_tree):
    legacy_ids = [
        "https://admin-shell.io/idta/EPD/LCIAIndicatorCode/1/0",
        "https://admin-shell.io/idta/EPD/LCIAIndicatorName/1/0",
        "https://admin-shell.io/idta/EPD/LCIAIndicator/1/0",
        "https://admin-shell.io/idta/EPD/LCIAResultEntry/1/0",
        "https://admin-shell.io/idta/EPD/LCIAResults/1/0",
        "https://admin-shell.io/idta/EPD/CharacterizationUnit/1/0"
    ]
    cds = template_tree.find(T("conceptDescriptions"))
    if cds is not None:
        for cd in cds:
            id_el = cd.find(T("id"))
            if id_el is not None:
                assert id_el.text not in legacy_ids, f"Found legacy CD: {id_el.text}"

def test_template_has_new_cds(template_tree):
    required_ids = [
        "https://wg-epd.example.com/draft/v1/IndicatorCode",
        "https://wg-epd.example.com/draft/v1/StageCode",
        "https://wg-epd.example.com/draft/v1/ResultCategory",
        "https://wg-epd.example.com/draft/v1/Unit",
        "https://wg-epd.example.com/draft/v1/BaseUnit"
    ]
    
    cds = template_tree.find(T("conceptDescriptions"))
    assert cds is not None
    
    found_ids = set()
    for cd in cds:
        id_el = cd.find(T("id"))
        if id_el is not None:
            found_ids.add(id_el.text)
            
    for req in required_ids:
        assert req in found_ids, f"Missing required ConceptDescription: {req}"

def test_instance_environmental_results_base_unit(instance_tree):
    # Ensure EnvironmentalResult instances have flat `unit` and optionally `baseUnit` SMC
    er_sml = None
    for sml in instance_tree.iter(T("submodelElementList")):
        if sml.find(T("idShort")) is not None and sml.find(T("idShort")).text == "EnvironmentalResults":
            er_sml = sml
            break
            
    assert er_sml is not None, "EnvironmentalResults SML not found"
    
    val = er_sml.find(T("value"))
    assert val is not None
    
    found_base_unit = False
    
    for smc in val.iter(T("submodelElementCollection")):
        if smc.find(T("idShort")) is not None:
            # Check properties
            smc_val = smc.find(T("value"))
            if smc_val is not None:
                has_unit = False
                for prop in smc_val.iter(T("property")):
                    ids = prop.find(T("idShort"))
                    if ids is not None and ids.text == "unit":
                        has_unit = True
                
                # Check for baseUnit SMC
                for child in smc_val.iter(T("submodelElementCollection")):
                    if child.find(T("idShort")) is not None and child.find(T("idShort")).text == "baseUnit":
                        found_base_unit = True
                        bu_val = child.find(T("value"))
                        assert bu_val is not None
                        has_bu_unit = False
                        has_bu_unit_id = False
                        for p in bu_val.iter(T("property")):
                            p_ids = p.find(T("idShort"))
                            if p_ids is not None:
                                if p_ids.text == "unit": has_bu_unit = True
                                if p_ids.text == "unitId": has_bu_unit_id = True
                        assert has_bu_unit, "baseUnit missing unit property"
                        assert has_bu_unit_id, "baseUnit missing unitId property"
                        
    assert found_base_unit, "No baseUnit SMC found in the entire instance, check generator script."
