"""
generate_wago_instance.py
=========================
Generates the fully-populated WAGO 221-422 EPD AAS instance AASX.

Strategy
--------
The script starts from the CORRECTED template AASX (already patched by
patch_template_aasx.py), then:

  1. Populates every field with source-derived or illustrative values.
  2. Builds all EnvironmentalResult SMC children from scratch (the template
     SML is empty by design — instance rows are not in a template).
  3. Removes any remaining legacy ``declaredUnit`` SMC.
  4. Packages the product image into the AASX zip.

Usage
-----
    conda run -n aas_env python scripts/generate_wago_instance.py

Output
------
    examples/wago-00001/wago-00001-v01-01-en-epd-submodel-instance.aasx
"""

from __future__ import annotations

import io
import json
import os
import zipfile
import xml.etree.ElementTree as ET
from typing import Optional

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TEMPLATE_AASX = os.path.join(
    REPO_ROOT, "model", "template", "epd-type-iii-submodel-template.aasx"
)
MAPPING_JSON = os.path.join(
    REPO_ROOT, "examples", "wago-00001", "mapping",
    "wago-00001-to-epd-submodel-mapping.json",
)
PRODUCT_IMAGE = os.path.join(
    REPO_ROOT, "examples", "wago-00001", "source",
    "ProductPicture_Wago_221_422.jpg",
)
OUTPUT_AASX = os.path.join(
    REPO_ROOT, "examples", "wago-00001",
    "wago-00001-v01-01-en-epd-submodel-instance.aasx",
)

IMAGE_AASX_PATH = "/aasx/files/ProductPicture_Wago_221_422.jpg"

NS_URI = "https://admin-shell.io/aas/3/0"
ET.register_namespace("aas", NS_URI)

LEGACY_DECLARED_UNIT_SEM = "https://admin-shell.io/idta/EPD/DeclaredUnit/1/0"
LEGACY_CD_IDS = {
    "https://admin-shell.io/idta/EPD/DeclaredUnit/1/0",
    "http://eclass.example.com/declaredUnit.qty",
    "http://eclass.example.com/declaredUnit.unit",
    "http://eclass.example.com/kgPerDeclaredUnit.qty",
    "http://eclass.example.com/kgCPerDeclaredUnit.qty",
    "http://eclass.example.com/kgCBiogenicPerDeclaredUnit.qty",
}

# ---------------------------------------------------------------------------
# Indicator catalogue
# ---------------------------------------------------------------------------
# (openEPD key, AAS idShort, resultCategory, unit, indicatorName)
IMPACT_INDICATORS: list[tuple[str, str, str, str, str, str]] = [
    ("gwp",          "GWP_total",      "GWP-total",    "ImpactIndicator", "kg CO2 eq.",   "Global Warming Potential (total)"),
    ("gwp-fossil",   "GWP_fossil",     "GWP-fossil",   "ImpactIndicator", "kg CO2 eq.",   "Global Warming Potential (fossil)"),
    ("gwp-biogenic", "GWP_biogenic",   "GWP-biogenic", "ImpactIndicator", "kg CO2 eq.",   "Global Warming Potential (biogenic)"),
    ("gwp-luluc",    "GWP_luluc",      "GWP-luluc",    "ImpactIndicator", "kg CO2 eq.",   "Global Warming Potential (land use and land use change)"),
    ("odp",          "ODP",            "ODP",          "ImpactIndicator", "kg CFC-11 eq.","Ozone Depletion Potential"),
    ("ap",           "AP",             "AP",           "ImpactIndicator", "mol H+ eq.",   "Acidification Potential"),
    ("ep-fresh",     "EP_freshwater",  "EP-freshwater","ImpactIndicator", "kg P eq.",     "Eutrophication Potential (freshwater)"),
    ("ep-marine",    "EP_marine",      "EP-marine",    "ImpactIndicator", "kg N eq.",     "Eutrophication Potential (marine)"),
    ("ep-terr",      "EP_terrestrial", "EP-terrestrial","ImpactIndicator", "mol N eq.",    "Eutrophication Potential (terrestrial)"),
    ("pocp",         "POCP",           "POCP",         "ImpactIndicator", "kg NMVOC eq.", "Photochemical Ozone Creation Potential"),
    ("adp-fossil",   "ADPF",           "ADPF",         "ImpactIndicator", "MJ",           "Abiotic Depletion Potential (fossil fuels)"),
    ("adp-elements", "ADPE",           "ADPE",         "ImpactIndicator", "kg Sb eq.",    "Abiotic Depletion Potential (elements)"),
]

# Indicators present in WAGO AASX model but absent from the openEPD source
# — values are ILLUSTRATIVE only; marked [ILLUSTRATIVE EXAMPLE]
ILLUSTRATIVE_INDICATORS: list[tuple[str, str, str, str, str]] = [
    ("WDP",     "WDP",     "ImpactIndicator", "m3 eq.",             "Water Deprivation Potential [ILLUSTRATIVE EXAMPLE]"),
    ("Total_PE","Total-PE","ImpactIndicator", "MJ",                 "Total Primary Energy [ILLUSTRATIVE EXAMPLE]"),
    ("PM",      "PM",      "ImpactIndicator", "disease incidence",  "Particulate Matter Formation [ILLUSTRATIVE EXAMPLE]"),
    ("IR",      "IR",      "ImpactIndicator", "kBq U-235 eq.",      "Ionising Radiation [ILLUSTRATIVE EXAMPLE]"),
    ("ETP_fw",  "ETP-fw",  "ImpactIndicator", "CTUe",               "Ecotoxicity (freshwater) [ILLUSTRATIVE EXAMPLE]"),
    ("HTP_c",   "HTP-c",   "ImpactIndicator", "CTUh",               "Human Toxicity Potential (cancer) [ILLUSTRATIVE EXAMPLE]"),
    ("HTP_nc",  "HTP-nc",  "ImpactIndicator", "CTUh",               "Human Toxicity Potential (non-cancer) [ILLUSTRATIVE EXAMPLE]"),
    ("SQP",     "SQP",     "ImpactIndicator", "dimensionless",      "Soil Quality Potential [ILLUSTRATIVE EXAMPLE]"),
]

# (openEPD key, AAS idShort, resultCategory, unit, indicatorName)
OUTPUT_FLOW_INDICATORS: list[tuple[str, str, str, str, str, str]] = [
    ("hwd",  "HWD",  "HWD",  "Waste",      "kg", "Hazardous Waste Disposed"),
    ("nhwd", "NHWD", "NHWD", "Waste",      "kg", "Non-Hazardous Waste Disposed"),
    ("rwd",  "RWD",  "RWD",  "Waste",      "kg", "Radioactive Waste Disposed"),
    ("cru",  "CRU",  "CRU",  "OutputFlow", "kg", "Components for Re-use"),
    ("mfr",  "MFR",  "MFR",  "OutputFlow", "kg", "Materials for Recycling"),
    ("mer",  "MER",  "MER",  "OutputFlow", "kg", "Materials for Energy Recovery"),
    ("ee",   "EE",   "EE",   "OutputFlow", "MJ", "Exported Energy"),
]

# Illustrative ResourceUse entries (source resource_uses = {})
ILLUSTRATIVE_RESOURCE_USE: list[tuple[str, str, str, str, str, dict]] = [
    (
        "PENRE", "PENRE", "ResourceUse", "MJ",
        "Non-renewable Primary Energy [ILLUSTRATIVE EXAMPLE]",
        {"A1-A3": ("Declared", 0.215), "A4": ("Declared", 0.008),
         "A5": ("Declared", 0.001), "B6": ("Declared", 0.950),
         "D": ("Declared", -0.010)},
    ),
    (
        "PERE", "PERE", "ResourceUse", "MJ",
        "Renewable Primary Energy [ILLUSTRATIVE EXAMPLE]",
        {"A1-A3": ("Declared", 0.042), "A4": ("Declared", 0.001),
         "A5": ("Declared", 0.0),   "B6": ("Declared", 0.005),
         "D": ("Declared", -0.002)},
    ),
]

# openEPD stage key -> AAS stageCode
STAGE_MAP: dict[str, str] = {
    "A1A2A3": "A1-A3", "A4": "A4", "A5": "A5",
    "B1": "B1", "B2": "B2", "B3": "B3", "B4": "B4",
    "B5": "B5", "B6": "B6", "B7": "B7",
    "C1": "C1", "C2": "C2", "C3": "C3", "C4": "C4",
    "D": "D",
}


# ---------------------------------------------------------------------------
# XML helpers
# ---------------------------------------------------------------------------

def T(local: str) -> str:  # noqa: N802 – short helper
    return "{" + NS_URI + "}" + local


def find_by_id(container: ET.Element, id_short: str) -> Optional[ET.Element]:
    """Return direct child of container whose idShort equals id_short."""
    for child in container:
        el = child.find(T("idShort"))
        if el is not None and el.text == id_short:
            return child
    return None


def get_val(sme: ET.Element) -> ET.Element:
    val = sme.find(T("value"))
    if val is None:
        val = ET.SubElement(sme, T("value"))
    return val


def set_prop(parent_val: ET.Element, id_short: str, value: str) -> bool:
    """Set Property value by idShort. Returns True if found."""
    el = find_by_id(parent_val, id_short)
    if el is None:
        return False
    v = el.find(T("value"))
    if v is None:
        v = ET.SubElement(el, T("value"))
    v.text = str(value)
    return True


def set_mlp(parent_val: ET.Element, id_short: str, lang: str, text: str) -> bool:
    """Set MLP value. Returns True if found."""
    el = find_by_id(parent_val, id_short)
    if el is None:
        return False
    val_el = el.find(T("value"))
    if val_el is None:
        val_el = ET.SubElement(el, T("value"))
    for lst in list(val_el):
        val_el.remove(lst)
    lst = ET.SubElement(val_el, T("langStringTextType"))
    ET.SubElement(lst, T("language")).text = lang
    ET.SubElement(lst, T("text")).text = text
    return True


def set_file(parent_val: ET.Element, id_short: str,
             path: str, ct: str) -> bool:
    el = find_by_id(parent_val, id_short)
    if el is None:
        return False
    v = el.find(T("value"))
    if v is None:
        v = ET.SubElement(el, T("value"))
    v.text = path
    ct_el = el.find(T("contentType"))
    if ct_el is not None:
        ct_el.text = ct
    return True


def make_sem(parent: ET.Element, url: str) -> None:
    sem = ET.SubElement(parent, T("semanticId"))
    ET.SubElement(sem, T("type")).text = "ExternalReference"
    keys = ET.SubElement(sem, T("keys"))
    key = ET.SubElement(keys, T("key"))
    ET.SubElement(key, T("type")).text = "GlobalReference"
    ET.SubElement(key, T("value")).text = url


def make_cardinality_qualifier(parent: ET.Element, card: str) -> None:
    quals = ET.SubElement(parent, T("qualifiers"))
    q = ET.SubElement(quals, T("qualifier"))
    ET.SubElement(q, T("type")).text = "SMT/Cardinality"
    ET.SubElement(q, T("valueType")).text = "xs:string"
    ET.SubElement(q, T("value")).text = card



def add_desc(parent, text):
    desc = ET.SubElement(parent, T("description"))
    ls = ET.SubElement(desc, T("langStringTextType"))
    ET.SubElement(ls, T("language")).text = "en"
    ET.SubElement(ls, T("text")).text = text

def make_simple_prop(parent_val: ET.Element, id_short: str,
                     sem_url: str, vtype: str, value: str,
                     category: str = "", desc: str = "",
                     value_id: str = "") -> ET.Element:
    prop = ET.SubElement(parent_val, T("property"))
    ET.SubElement(prop, T("idShort")).text = id_short
    if category:
        ET.SubElement(prop, T("category")).text = category
    make_sem(prop, sem_url)
    make_cardinality_qualifier(prop, "One")
    ET.SubElement(prop, T("valueType")).text = vtype
    ET.SubElement(prop, T("value")).text = value
    if desc:
        add_desc(prop, desc)
        
    if value_id:
        vid = ET.SubElement(prop, T("valueId"))
        ET.SubElement(vid, T("type")).text = "ExternalReference"
        keys = ET.SubElement(vid, T("keys"))
        k1 = ET.SubElement(keys, T("key"))
        ET.SubElement(k1, T("type")).text = "GlobalReference"
        ET.SubElement(k1, T("value")).text = value_id
        
    return prop


# ---------------------------------------------------------------------------
# StageValue builder
# ---------------------------------------------------------------------------

def build_stage_value(stage_code: str, status: str,
                      value: Optional[float]) -> ET.Element:
    smc = ET.Element(T("submodelElementCollection"))
    ET.SubElement(smc, T("idShort")).text = "sv_" + stage_code
    make_sem(smc, "https://wg-epd.example.com/draft/v1/StageValue")
    make_cardinality_qualifier(smc, "ZeroToMany")
    val = ET.SubElement(smc, T("value"))

    make_simple_prop(val, "stageCode",
                     "https://wg-epd.example.com/draft/v1/StageCode",
                     "xs:string", stage_code, "PARAMETER",
                     value_id=f"https://wg-epd.example.com/draft/v1/Value/{stage_code}")
    make_simple_prop(val, "valueStatus",
                     "https://wg-epd.example.com/draft/v1/ValueStatus",
                     "xs:string", status, "PARAMETER")
    if value is not None:
        make_simple_prop(val, "value",
                         "https://wg-epd.example.com/draft/v1/IndicatorValue",
                         "xs:double", repr(float(value)), "PARAMETER")
    return smc


def build_stage_values_from_source(source_data: dict) -> list[ET.Element]:
    """Build StageValue SMCs for all stages from openEPD source dict."""
    result = []
    for epd_key, aas_stage in STAGE_MAP.items():
        stage_entry = source_data.get(epd_key)
        if stage_entry is None:
            result.append(build_stage_value(aas_stage, "NotDeclared", None))
        elif isinstance(stage_entry, dict):
            mean = stage_entry.get("mean")
            if mean is None:
                result.append(build_stage_value(aas_stage, "NotDeclared", None))
            else:
                result.append(build_stage_value(aas_stage, "Declared", float(mean)))
        else:
            result.append(build_stage_value(aas_stage, "NotDeclared", None))
    return result


def build_illustrative_stage_values(stages: dict) -> list[ET.Element]:
    result = []
    for stage_code, (status, value) in stages.items():
        result.append(build_stage_value(stage_code, status, value))
    return result


# Default illustrative stages for indicators with no source data
def _default_illustrative_stages() -> dict:
    return {
        "A1-A3": ("Declared", 0.0),
        "A4":   ("Declared", 0.0),
        "A5":   ("Declared", 0.0),
        "B1":   ("Declared", 0.0), "B2": ("Declared", 0.0),
        "B3":   ("Declared", 0.0), "B4": ("Declared", 0.0),
        "B5":   ("Declared", 0.0), "B6": ("Declared", 0.0),
        "B7":   ("Declared", 0.0),
        "C1":   ("NotDeclared", None), "C2": ("NotDeclared", None),
        "C3":   ("NotDeclared", None), "C4": ("NotDeclared", None),
        "D":    ("Declared", 0.0),
    }


# ---------------------------------------------------------------------------
# EnvironmentalResult SMC builder
# ---------------------------------------------------------------------------

def build_environmental_result_smc(
    id_short: str,
    result_category: str,
    indicator_code: str,
    indicator_name: str,
    unit: str,
    unit_id: str,
    base_unit: str,
    base_unit_id: str,
    stage_values: list[ET.Element],
) -> ET.Element:
    smc = ET.Element(T("submodelElementCollection"))
    ET.SubElement(smc, T("idShort")).text = id_short
    make_sem(smc, "https://wg-epd.example.com/draft/v1/EnvironmentalResult")
    make_cardinality_qualifier(smc, "ZeroToMany")

    val = ET.SubElement(smc, T("value"))

    make_simple_prop(val, "resultCategory",
                     "https://wg-epd.example.com/draft/v1/ResultCategory",
                     "xs:string", result_category, "PARAMETER",
                     value_id=f"https://wg-epd.example.com/draft/v1/Value/{result_category}")
    make_simple_prop(val, "indicatorCode",
                     "https://wg-epd.example.com/draft/v1/IndicatorCode",
                     "xs:string", indicator_code, "PARAMETER",
                     value_id=f"https://wg-epd.example.com/draft/v1/Indicator/{indicator_code}")
    make_simple_prop(val, "indicatorName",
                     "https://wg-epd.example.com/draft/v1/IndicatorName",
                     "xs:string", indicator_name, "PARAMETER")
    make_simple_prop(val, "unit",
                     "https://wg-epd.example.com/draft/v1/Unit",
                     "xs:string", unit, "PARAMETER")
    if unit_id:
        make_simple_prop(val, "unitId",
                         "https://wg-epd.example.com/draft/v1/UnitId",
                         "xs:string", unit_id, "PARAMETER")

    if base_unit and base_unit_id:
        bu_smc = ET.SubElement(val, T("submodelElementCollection"))
        ET.SubElement(bu_smc, T("idShort")).text = "baseUnit"
        make_sem(bu_smc, "https://wg-epd.example.com/draft/v1/BaseUnit")
        make_cardinality_qualifier(bu_smc, "ZeroToOne")
        bu_val = ET.SubElement(bu_smc, T("value"))
        
        make_simple_prop(bu_val, "unit",
                         "https://wg-epd.example.com/draft/v1/Unit",
                         "xs:string", base_unit, "PARAMETER")
        make_simple_prop(bu_val, "unitId",
                         "https://wg-epd.example.com/draft/v1/UnitId",
                         "xs:string", base_unit_id, "PARAMETER")

    # stageValues SML
    sv_sml = ET.SubElement(val, T("submodelElementList"))
    ET.SubElement(sv_sml, T("idShort")).text = "stageValues"
    add_desc(sv_sml, "List of values across lifecycle phases.")
    make_sem(sv_sml, "https://wg-epd.example.com/draft/v1/StageValues")
    make_cardinality_qualifier(sv_sml, "One")
    ET.SubElement(sv_sml, T("typeValueListElement")).text = \
        "SubmodelElementCollection"
    sem_list_el = ET.SubElement(sv_sml, T("semanticIdListElement"))
    ET.SubElement(sem_list_el, T("type")).text = "ExternalReference"
    sv_keys = ET.SubElement(sem_list_el, T("keys"))
    sv_key = ET.SubElement(sv_keys, T("key"))
    ET.SubElement(sv_key, T("type")).text = "GlobalReference"
    ET.SubElement(sv_key, T("value")).text = \
        "https://wg-epd.example.com/draft/v1/StageValue"

    sv_val = ET.SubElement(sv_sml, T("value"))
    for sv in stage_values:
        sv_val.append(sv)

    return smc


# ---------------------------------------------------------------------------
# Population functions
# ---------------------------------------------------------------------------

def remove_legacy(sme_root: ET.Element, cd_root: Optional[ET.Element]) -> None:
    print("\n[1] Removing legacy declaredUnit and architecture regressions...")
    removed = 0

    def _rm_from(container: ET.Element) -> int:
        n = 0
        for child in list(container):
            id_el = child.find(T("idShort"))
            if id_el is None or id_el.text != "declaredUnit":
                continue
            sem_el = child.find(
                T("semanticId") + "/" + T("keys") + "/" + T("key") + "/" + T("value")
            )
            if sem_el is not None and sem_el.text == LEGACY_DECLARED_UNIT_SEM:
                container.remove(child)
                print("    [REMOVED] declaredUnit SMC")
                n += 1
        return n

    removed += _rm_from(sme_root)

    # Inside manufacturerProduct
    mp = find_by_id(sme_root, "manufacturerProduct")
    if mp is not None:
        mp_val = mp.find(T("value"))
        if mp_val is not None:
            removed += _rm_from(mp_val)
            # ContentDeclaration regression protection: move/remove biogenicCarbonContent from manufacturerProduct
            bcc = find_by_id(mp_val, "biogenicCarbonContent")
            if bcc is not None:
                mp_val.remove(bcc)
                print("    [REMOVED] biogenicCarbonContent from manufacturerProduct")

    # ContentDeclaration fix
    cd = find_by_id(sme_root, "ContentDeclaration")
    if cd is not None:
        cd_val = cd.find(T("value"))
        if cd_val is not None:
            for child in list(cd_val):
                id_el = child.find(T("idShort"))
                if id_el is not None and id_el.text in ("biogenicCarbonContentProduct", "biogenicCarbonContentPackaging"):
                    cd_val.remove(child)
                    print(f"    [REMOVED] ContentDeclaration > {id_el.text} (flat)")
            
            # Ensure biogenicCarbonContent SMC exists
            bcc = find_by_id(cd_val, "biogenicCarbonContent")
            if bcc is None:
                bcc = ET.SubElement(cd_val, T("submodelElementCollection"))
                ET.SubElement(bcc, T("idShort")).text = "biogenicCarbonContent"
                bcc_v = ET.SubElement(bcc, T("value"))
                # Also create the properties since they were removed from flat representation
                make_simple_prop(bcc_v, "biogenicCarbonContentProduct", "https://wg-epd.example.com/draft/v1/BiogenicCarbonContentProduct", "xs:decimal", "")
                make_simple_prop(bcc_v, "biogenicCarbonContentPackaging", "https://wg-epd.example.com/draft/v1/BiogenicCarbonContentPackaging", "xs:decimal", "")

    # LCAMethodology fix
    lca = find_by_id(sme_root, "LCAMethodology")
    if lca is not None:
        lca_val = lca.find(T("value"))
        if lca_val is not None:
            for child in list(lca_val):
                id_el = child.find(T("idShort"))
                if id_el is not None:
                    if id_el.text in ("referenceFlow.id", "referenceFlow.amount", "pictogramSource", "flowDiagramSource", "dataSetValidUntil", "technicalPurpose"):
                        lca_val.remove(child)
                        print(f"    [REMOVED] LCAMethodology > {id_el.text}")
                    elif id_el.text == "referenceYear":
                        id_el.text = "lcaReferenceYear"
                        print("    [RENAMED] referenceYear -> lcaReferenceYear")
                    elif id_el.text == "location":
                        id_el.text = "geographicalScope"
                        print("    [RENAMED] location -> geographicalScope")
                    elif id_el.text == "energyModel":
                        id_el.text = "lcaEnergyModel"
                        print("    [RENAMED] energyModel -> lcaEnergyModel")

    # EPDScope fix
    scope = find_by_id(sme_root, "EPDScope")
    if scope is not None:
        scope_val = scope.find(T("value"))
        if scope_val is not None:
            for child in list(scope_val):
                id_el = child.find(T("idShort"))
                if id_el is not None and id_el.text == "sourceDeclarationReference":
                    scope_val.remove(child)
                    print("    [REMOVED] EPDScope > sourceDeclarationReference")

    if cd_root is not None:
        for cd_el in list(cd_root):
            id_el = cd_el.find(T("id"))
            if id_el is not None and id_el.text in LEGACY_CD_IDS:
                cd_root.remove(cd_el)
                print("    [REMOVED] ConceptDescription " + id_el.text)
                removed += 1

    print("    Total removed: " + str(removed))


def populate_identification_publication(sme_root: ET.Element) -> None:
    print("\n[2] identificationPublication...")
    ip = find_by_id(sme_root, "identificationPublication")
    if ip is None:
        print("    [WARN] not found")
        return
    v = get_val(ip)
    set_prop(v, "programOperatorVersion", "01.01")
    set_prop(v, "dateOfIssue", "2026-02-01")
    set_prop(v, "validUntil", "2031-02-01")
    set_prop(v, "sourceDataFormat", "PEP Ecopassport PDF")
    
    dec_url = (
        "https://register.pep-ecopassport.org/files/mbesqrsCBZbWbKJq6-kJ3r0ozZDJ7D4099iCaN_Rt63LD83yDlmtwusfITWNToUXhIjPv0yT1zYi7_69uxR891RZGs0wdVFSdHlY0eXUbqx1BRv7sT36QfD7H5J6_dlF2XQpEedt0ppT8_9ON1jCqCPDV3O0VtnNNvjkK_7CWzm11avBD_b_ZJYuLE2Cy0mE_0Z7ZfyYUR2tuLz5N8dApJj3rAPc9Njm_ioFnU4Xua4EJMtRVPOEl50Tr6LO-1kmGiT3z6l_2Z03dzLc2yiork7und4_zIuGix56ye-Y5xjIR18rUTRItZ_BSUqL5QyanzC06YUyS9VXVt_jOSC-6NSPWh1_Ww_W4JiEnzFIOYTcZ6owJSub5iAUSQIm-WMIYW-b3pPnni-9m2Pn_VtVd1hdfQcXe8ag2QatOp7hDOyFKIjmVEw55F643MbnG_BASXZss3o_kJKa5xgxzYSLfjsNXWz2bFvq-vRz-ycSpa0Ua_jlC6NfVAErOQ7ILH5ArE_2Fzef2MQWukiLTmo3kuk4lYZnvBSsnpP1070x51JLbYfLcFkqSs_f5RUoDaariV9wj-gpc8rTRc_99ojmsAlmVyfV4sGIoIXvXc4njdfRq2Sodf_pzQGrWXpcxBrSEZ3TkGRQbluV2DN4IsXiw5pXQ1qaOyos_if5SNFDv6D-A4cb0cqkdB4W_QNvNqLG55W9453q980rYvpI24-LOcqXRyyg0zRTo1axZRKZJX5U93b2I0b9i4Ud1dcF3FtV3PMp-1Tu-e-ZE1BQpOf8V-VjZ_6sY_6VI44EvLSjDv4fUor-FXPb4Fno2XuVQGvxTNU18LpqCMz9z5Lm4y_N8u_gRxSwKK2W4oTcfvLLJBAGysozpVU6xDUUOpsPMrYPonMwmzec3qKQW-ZYLhcvIisHEFammdFQp5Wl-YurEfVhQv6IB_UAUnKzciTm42Ph4yii-YlaN63R8NKNyDn42w"
    )
    set_prop(v, "declarationUrl", dec_url)

    # documentIds
    doc_ids = find_by_id(v, "documentIds")
    if doc_ids is not None:
        di_val = doc_ids.find(T("value"))
        if di_val is not None and len(list(di_val)) == 0:
            di_val.text = None  # clear self-closing
            smc = ET.SubElement(di_val, T("submodelElementCollection"))
            ET.SubElement(smc, T("idShort")).text = "documentId_0"
            smc_v = ET.SubElement(smc, T("value"))
            make_simple_prop(smc_v, "documentDomainId",
                             "https://admin-shell.io/vdi/2770/1/0/DocumentDomainId",
                             "xs:string", "PEP ecopassport")
            make_simple_prop(smc_v, "documentIdentifier",
                             "https://admin-shell.io/vdi/2770/1/0/DocumentId",
                             "xs:string", "WAGO-00001-V01.01-EN")
            make_simple_prop(smc_v, "documentIsPrimary",
                             "https://admin-shell.io/idta/EPD/DocumentIsPrimary/1/0",
                             "xs:boolean", "true")

    # languages
    langs = find_by_id(v, "languages")
    if langs is not None:
        la_val = langs.find(T("value"))
        if la_val is not None and len(list(la_val)) == 0:
            la_val.text = None
            for i, lang_code in enumerate(["DE", "EN", "FR"]):
                prop = ET.SubElement(la_val, T("property"))
                ET.SubElement(prop, T("idShort")).text = str(i)
                ET.SubElement(prop, T("valueType")).text = "xs:string"
                ET.SubElement(prop, T("value")).text = lang_code

    print("    OK")


def populate_program_operator_verification(sme_root: ET.Element) -> None:
    print("\n[3] programOperatorVerification...")
    pov = find_by_id(sme_root, "programOperatorVerification")
    if pov is None:
        print("    [WARN] not found")
        return
    v = get_val(pov)

    # Structure:
    #   programOperator [SMC] -> Company [property], EmailAddress [SMC] -> EmailAddress [property]
    #   thirdPartyVerifier [SMC] -> verifierAccreditationId [property], verificationStatementUrl [property]
    #   epdDeveloper [SMC] -> Company [MLP]
    #   verificationType [property]
    #   verificationDate [property]

    # programOperator
    po = find_by_id(v, "programOperator")
    if po is not None:
        po_v = get_val(po)
        set_prop(po_v, "Company", "Association P.E.P (PEP ecopassport)")
        # EmailAddress nested SMC
        ea_smc = find_by_id(po_v, "EmailAddress")
        if ea_smc is not None:
            ea_v = get_val(ea_smc)
            set_prop(ea_v, "EmailAddress", "contact@pep-ecopassport.org")
        print("    programOperator: OK")

    # thirdPartyVerifier
    tpv = find_by_id(v, "thirdPartyVerifier")
    if tpv is not None:
        tpv_v = get_val(tpv)
        set_prop(tpv_v, "verifierAccreditationId", "WAP-001")
        print("    thirdPartyVerifier: OK")

    # epdDeveloper
    dev = find_by_id(v, "epdDeveloper")
    if dev is not None:
        dev_v = get_val(dev)
        set_mlp(dev_v, "Company", "en", "WAGO GmbH & Co. KG")
        print("    epdDeveloper: OK")

    # verificationType / verificationDate (flat properties)
    set_prop(v, "verificationType", "ThirdPartyVerification")
    set_prop(v, "verificationDate", "2026-02-01")

    print("    OK")


def populate_manufacturer_product(sme_root: ET.Element, mapping: dict) -> None:
    print("\n[4] manufacturerProduct...")
    mp = find_by_id(sme_root, "manufacturerProduct")
    if mp is None:
        print("    [WARN] not found")
        return
    v = get_val(mp)

    product_desc = mapping.get("product_description", "")
    kg_per_du = mapping.get("kg_per_declared_unit", {}).get("qty", 0.001958)
    service_life = mapping.get("product_service_life_years", 30)
    product_sku = mapping.get("product_sku", "221-422")
    product_name = mapping.get("product_name", "221 Series / Splicing Connector with Levers")

    set_mlp(v, "manufacturerName", "en", "WAGO GmbH & Co. KG")
    set_mlp(v, "productName", "en", product_name)
    set_prop(v, "productArticleNumberOfManufacturer", product_sku)
    set_mlp(v, "productDescription", "en", product_desc if product_desc else
            "The function of the product is to connect power transmission cables "
            "together, or to connect them to equipment, for one unit and its "
            "packaging, under operating conditions identical to those of the cable: "
            "1 ampere (A) over 30 years, with a use rate of 70%.")
    set_mlp(v, "manufacturingDescription", "en",
            "Manufactured at WAGO production facilities in Minden, Germany "
            "(Hansastrasse 27, 32423 Minden). "
            "[Source: WAGO PEP ecopassport CQDPP5FX]")
    set_prop(v, "massPerDeclaredUnit", str(kg_per_du))
    set_prop(v, "referenceServiceLife", str(service_life))

    # productImage
    set_file(v, "productImage", IMAGE_AASX_PATH, "image/jpeg")

    # applicableJurisdictions
    aj = find_by_id(v, "applicableJurisdictions")
    if aj is not None:
        aj_val = aj.find(T("value"))
        if aj_val is not None and len(list(aj_val)) == 0:
            aj_val.text = None
            prop = ET.SubElement(aj_val, T("property"))
            ET.SubElement(prop, T("idShort")).text = "0"
            ET.SubElement(prop, T("valueType")).text = "xs:string"
            ET.SubElement(prop, T("value")).text = "001"

    # manufacturingSites
    ms = find_by_id(v, "manufacturingSites")
    if ms is not None:
        ms_val = ms.find(T("value"))
        if ms_val is not None and len(list(ms_val)) == 0:
            ms_val.text = None
            
            # Example 1: Normal fixed manufacturing site
            site1 = ET.SubElement(ms_val, T("submodelElementCollection"))
            ET.SubElement(site1, T("idShort")).text = "ManufacturingSite_01"
            add_desc(site1, "A physical manufacturing site associated with the product.")
            site1_v = ET.SubElement(site1, T("value"))
            
            # Nested SiteIdentifiers SML
            sids1 = ET.SubElement(site1_v, T("submodelElementList"))
            ET.SubElement(sids1, T("idShort")).text = "SiteIdentifiers"
            add_desc(sids1, "List of explicit identifiers for the site.")
            ET.SubElement(sids1, T("typeValueListElement")).text = "SubmodelElementCollection"
            sids1_v = ET.SubElement(sids1, T("value"))
            
            # Nested SiteIdentifier SMC
            sid1 = ET.SubElement(sids1_v, T("submodelElementCollection"))
            ET.SubElement(sid1, T("idShort")).text = "SiteIdentifier_01"
            add_desc(sid1, "An explicit site identifier.")
            sid1_v = ET.SubElement(sid1, T("value"))
            make_simple_prop(sid1_v, "identifierScheme", "https://wg-epd.example.com/draft/v1/SiteIdentifier/Scheme", "xs:string", "Internal", desc="Identifier scheme.")
            make_simple_prop(sid1_v, "identifierValue", "https://wg-epd.example.com/draft/v1/SiteIdentifier/Value", "xs:string", "WAGO-Minden-01", desc="Value of the identifier.")

            make_simple_prop(site1_v, "siteName", "https://wg-epd.example.com/draft/v1/ManufacturingSite/Name", "xs:string", "WAGO Minden Plant", desc="Human-readable site name.")
            make_simple_prop(site1_v, "siteType", "https://wg-epd.example.com/draft/v1/ManufacturingSite/Type", "xs:string", "Fixed", desc="Type of the site (e.g., Fixed, Mobile).")
            make_simple_prop(site1_v, "siteOperator", "https://wg-epd.example.com/draft/v1/ManufacturingSite/Operator", "xs:string", "WAGO GmbH & Co. KG", desc="Legal entity operating manufacturing activities at the specific site.")
            
            loc1 = ET.SubElement(site1_v, T("submodelElementCollection"))
            ET.SubElement(loc1, T("idShort")).text = "Location"
            add_desc(loc1, "Physical/geographical site description.")
            loc1_v = ET.SubElement(loc1, T("value"))
            make_simple_prop(loc1_v, "countryCode", "https://wg-epd.example.com/draft/v1/Location/CountryCode", "xs:string", "DE", desc="Physical country.")
            make_simple_prop(loc1_v, "region", "https://wg-epd.example.com/draft/v1/Location/Region", "xs:string", "Nordrhein-Westfalen", desc="Administrative or geographical subdivision.")
            make_simple_prop(loc1_v, "locality", "https://wg-epd.example.com/draft/v1/Location/Locality", "xs:string", "Minden", desc="City / municipality / comparable locality.")
            # Note: exact latitude/longitude and locationCode are EXTERNALLY ENRICHED EXAMPLE DATA here.
            make_simple_prop(loc1_v, "latitude", "https://wg-epd.example.com/draft/v1/Location/Latitude", "xs:decimal", "52.2882", desc="Decimal geographic latitude coordinate.")
            make_simple_prop(loc1_v, "longitude", "https://wg-epd.example.com/draft/v1/Location/Longitude", "xs:decimal", "8.9161", desc="Decimal geographic longitude coordinate.")
            
            # Nested LocationCodes SML
            lcodes1 = ET.SubElement(loc1_v, T("submodelElementList"))
            ET.SubElement(lcodes1, T("idShort")).text = "LocationCodes"
            add_desc(lcodes1, "List of coded geographical representations.")
            ET.SubElement(lcodes1, T("typeValueListElement")).text = "SubmodelElementCollection"
            lcodes1_v = ET.SubElement(lcodes1, T("value"))
            
            # Nested LocationCode SMC
            lcode1 = ET.SubElement(lcodes1_v, T("submodelElementCollection"))
            ET.SubElement(lcode1, T("idShort")).text = "LocationCode_01"
            add_desc(lcode1, "A coded geographical representation.")
            lcode1_v = ET.SubElement(lcode1, T("value"))
            make_simple_prop(lcode1_v, "codingSystem", "https://wg-epd.example.com/draft/v1/LocationCode/System", "xs:string", "Open Location Code", desc="The geographical coding system.")
            make_simple_prop(lcode1_v, "code", "https://wg-epd.example.com/draft/v1/LocationCode/Code", "xs:string", "9F4G7WQX+7Q", desc="The actual geographical code.")

            # Example 2: Contract manufacturing / mobile site (illustrative)
            # Note: All data below is ILLUSTRATIVE.
            site2 = ET.SubElement(ms_val, T("submodelElementCollection"))
            ET.SubElement(site2, T("idShort")).text = "ManufacturingSite_02"
            add_desc(site2, "A physical manufacturing site associated with the product.")
            site2_v = ET.SubElement(site2, T("value"))
            
            # Nested SiteIdentifiers SML
            sids2 = ET.SubElement(site2_v, T("submodelElementList"))
            ET.SubElement(sids2, T("idShort")).text = "SiteIdentifiers"
            add_desc(sids2, "List of explicit identifiers for the site.")
            ET.SubElement(sids2, T("typeValueListElement")).text = "SubmodelElementCollection"
            sids2_v = ET.SubElement(sids2, T("value"))
            
            # Nested SiteIdentifier SMC
            sid2 = ET.SubElement(sids2_v, T("submodelElementCollection"))
            ET.SubElement(sid2, T("idShort")).text = "SiteIdentifier_01"
            add_desc(sid2, "An explicit site identifier.")
            sid2_v = ET.SubElement(sid2, T("value"))
            make_simple_prop(sid2_v, "identifierScheme", "https://wg-epd.example.com/draft/v1/SiteIdentifier/Scheme", "xs:string", "Internal", desc="Identifier scheme.")
            make_simple_prop(sid2_v, "identifierValue", "https://wg-epd.example.com/draft/v1/SiteIdentifier/Value", "xs:string", "Contractor-Mob-01", desc="Value of the identifier.")

            make_simple_prop(site2_v, "siteName", "https://wg-epd.example.com/draft/v1/ManufacturingSite/Name", "xs:string", "Contract Manufacturer XYZ Mobile Plant (Illustrative)", desc="Human-readable site name.")
            make_simple_prop(site2_v, "siteType", "https://wg-epd.example.com/draft/v1/ManufacturingSite/Type", "xs:string", "Mobile", desc="Type of the site (e.g., Fixed, Mobile).")
            make_simple_prop(site2_v, "siteOperator", "https://wg-epd.example.com/draft/v1/ManufacturingSite/Operator", "xs:string", "Contract Manufacturer XYZ", desc="Legal entity operating manufacturing activities at the specific site.")
            
            loc2 = ET.SubElement(site2_v, T("submodelElementCollection"))
            ET.SubElement(loc2, T("idShort")).text = "Location"
            add_desc(loc2, "Physical/geographical site description.")
            loc2_v = ET.SubElement(loc2, T("value"))
            make_simple_prop(loc2_v, "countryCode", "https://wg-epd.example.com/draft/v1/Location/CountryCode", "xs:string", "FR", desc="Physical country.")
            make_simple_prop(loc2_v, "region", "https://wg-epd.example.com/draft/v1/Location/Region", "xs:string", "Grand Est")

    print("    OK")


def populate_lca_methodology(sme_root: ET.Element) -> None:
    print("\n[5] LCAMethodology...")
    lca = find_by_id(sme_root, "LCAMethodology")
    if lca is None:
        print("    [WARN] not found")
        return
    v = get_val(lca)

    # Set whatever fields exist in the template
    set_prop(v, "lcaReferenceYear", "2023")
    set_prop(v, "lcaEnergyModel", "DE")
    set_prop(v, "geographicalScope", "GLO")
    set_prop(v, "referenceYearStart", "2023")
    set_prop(v, "referenceYearEnd", "2023")
    set_prop(v, "lcaSoftware", "SimaPro 9")
    set_prop(v, "lcaSoftwareName", "SimaPro 9")
    set_prop(v, "lcaDatabase", "ecoinvent 3.9.1")
    set_prop(v, "lcaDatabaseName", "ecoinvent 3.9.1")
    set_prop(v, "allocationApproach", "PhysicalAllocation")
    set_prop(v, "cutOffCriteria", "PEP ecopassport cut-off rules applied")
    set_prop(v, "dataQualityComment", "Plant-specific and product-specific data used for manufacturing stage.")
    set_mlp(v, "systemBoundaryDescription", "en",
            "Cradle to gate with options (A1-A3, A4, A5, B1-B7, D). "
            "End-of-life stages C1-C4 not assessed per PEP ecopassport rules.")
    set_mlp(v, "characterisationFactorSource", "en",
            "EF 3.0 characterisation factors")
    set_prop(v, "characterisationFactorDataset", "EF 3.0")
    set_prop(v, "infrastructureProcesses", "false")
    set_prop(v, "geographicRepresentativeness", "Global / European")

    # Print existing fields
    for child in v:
        id_el = child.find(T("idShort"))
        if id_el is not None:
            tag_name = child.tag.split("}")[-1]
            val_el = child.find(T("value"))
            if val_el is not None and len(list(val_el)) == 0:
                print("    field: " + id_el.text + " [" + tag_name + "] = " + str(val_el.text or ""))

    # DeclaredStages
    ds = find_by_id(v, "DeclaredStages")
    if ds is not None:
        ds_val = ds.find(T("value"))
        if ds_val is not None and len(list(ds_val)) == 0:
            ds_val.text = None
            for code, status in [
                ("A1-A3", "Assessed"), ("A4", "Assessed"), ("A5", "Assessed"),
                ("B1", "Assessed"), ("B2", "Assessed"), ("B3", "Assessed"),
                ("B4", "Assessed"), ("B5", "Assessed"), ("B6", "Assessed"),
                ("B7", "Assessed"),
                ("C1", "NotAssessed"), ("C2", "NotAssessed"),
                ("C3", "NotAssessed"), ("C4", "NotAssessed"),
                ("D", "Assessed"),
            ]:
                sd = ET.SubElement(ds_val, T("submodelElementCollection"))
                ET.SubElement(sd, T("idShort")).text = "stage_" + code.replace("-", "_")
                sd_v = ET.SubElement(sd, T("value"))
                make_simple_prop(sd_v, "stageCode", "https://wg-epd.example.com/draft/v1/StageCode", "xs:string", code)
                make_simple_prop(sd_v, "stageStatus", "https://wg-epd.example.com/draft/v1/StageStatus", "xs:string", status)
    print("    OK")


def populate_canonical_declared_unit(sme_root: ET.Element, mapping: dict) -> None:
    print("\n[7] DeclaredUnit (canonical)...")
    du_el = find_by_id(sme_root, "DeclaredUnit")
    if du_el is None:
        print("    [WARN] not found")
        return
    du_v = get_val(du_el)
    du_src = mapping.get("declared_unit", {"qty": 1, "unit": "item"})
    kg_per_du = mapping.get("kg_per_declared_unit", {}).get("qty", 0.001958)
    set_prop(du_v, "quantity", str(du_src.get("qty", 1)))
    set_prop(du_v, "unit", du_src.get("unit", "item"))
    # description
    desc = find_by_id(du_v, "description")
    if desc is not None:
        desc_v = desc.find(T("value"))
        if desc_v is None:
            desc_v = ET.SubElement(desc, T("value"))
        for lst in list(desc_v):
            desc_v.remove(lst)
        lst = ET.SubElement(desc_v, T("langStringTextType"))
        ET.SubElement(lst, T("language")).text = "en"
        ET.SubElement(lst, T("text")).text = (
            "1 item (product unit + packaging). "
            "Mass = " + str(kg_per_du) + " kg per declared unit."
        )
    print("    quantity=" + str(du_src.get("qty", 1)) +
          "  unit=" + str(du_src.get("unit", "item")))
    print("    OK")


def populate_functional_unit(sme_root: ET.Element) -> None:
    print("\n[8] FunctionalUnit (illustrative)...")

    def _fill_fu(fu_el: ET.Element) -> None:
        fu_v = get_val(fu_el)
        set_prop(fu_v, "quantity", "1")
        set_prop(fu_v, "unit", "A")
        desc = find_by_id(fu_v, "description")
        if desc is not None:
            desc_v = desc.find(T("value"))
            if desc_v is None:
                desc_v = ET.SubElement(desc, T("value"))
            for lst in list(desc_v):
                desc_v.remove(lst)
            lst = ET.SubElement(desc_v, T("langStringTextType"))
            ET.SubElement(lst, T("language")).text = "en"
            ET.SubElement(lst, T("text")).text = (
                "1 ampere (A) continuous current over 30 years at 70% use rate, "
                "in accordance with applicable standards. "
                "[ILLUSTRATIVE — functional unit not declared in PEP ecopassport source]"
            )

    fu = find_by_id(sme_root, "FunctionalUnit")
    if fu is not None:
        _fill_fu(fu)
        print("    OK (top-level)")
    else:
        print("    [WARN] top-level FunctionalUnit not found")

    # Also look inside EPDScope
    scope = find_by_id(sme_root, "EPDScope")
    if scope is not None:
        scope_v = scope.find(T("value"))
        if scope_v is not None:
            fu2 = find_by_id(scope_v, "FunctionalUnit")
            if fu2 is not None:
                _fill_fu(fu2)
                print("    OK (inside EPDScope)")


def populate_epd_scope(sme_root: ET.Element) -> None:
    print("\n[9] EPDScope...")
    scope = find_by_id(sme_root, "EPDScope")
    if scope is None:
        print("    [WARN] not found")
        return
    scope_v = get_val(scope)
    set_prop(scope_v, "scopeType", "Instance")
    set_mlp(scope_v, "scopeDescription", "en",
            "Single-product EPD for WAGO 221-422 (2-conductor splicing connector "
            "with lever, 1 item + packaging). "
            "Scope: cradle-to-gate with options (A1-A3, A4, A5, B1-B7, D).")
    cpr = find_by_id(scope_v, "coveredProductReferences")
    if cpr is not None:
        cpr_v = cpr.find(T("value"))
        if cpr_v is not None and len(list(cpr_v)) == 0:
            cpr_v.text = None
            variants = ["221-412", "221-413", "221-415", "221-422", "221-423", "221-425"]
            for i, var in enumerate(variants):
                prop = ET.SubElement(cpr_v, T("property"))
                ET.SubElement(prop, T("idShort")).text = str(i)
                ET.SubElement(prop, T("valueType")).text = "xs:string"
                ET.SubElement(prop, T("value")).text = var
    print("    OK")


def populate_content_declaration(sme_root: ET.Element, mapping: dict) -> None:
    print("\n[10] ContentDeclaration...")
    cd_el = find_by_id(sme_root, "ContentDeclaration")
    if cd_el is None:
        print("    [WARN] not found")
        return
    cd_v = get_val(cd_el)
    kg_per_du = mapping.get("kg_per_declared_unit", {}).get("qty", 0.001958)
    set_prop(cd_v, "productMass", str(kg_per_du))
    set_prop(cd_v, "recycledContentPercentage", "0.0")

    bcc = find_by_id(cd_v, "biogenicCarbonContent")
    if bcc is not None:
        bcc_v = bcc.find(T("value"))
        if bcc_v is not None:
            # We don't have biogenic carbon data for the WAGO instance, use 0.0
            if not set_prop(bcc_v, "biogenicCarbonContentProduct", "0.0"):
                make_simple_prop(bcc_v, "biogenicCarbonContentProduct", "https://wg-epd.example.com/draft/v1/BiogenicCarbonContentProduct", "xs:decimal", "0.0")
            if not set_prop(bcc_v, "biogenicCarbonContentPackaging", "0.0"):
                make_simple_prop(bcc_v, "biogenicCarbonContentPackaging", "https://wg-epd.example.com/draft/v1/BiogenicCarbonContentPackaging", "xs:decimal", "0.0")
    print("    OK")


def populate_environmental_results(sme_root: ET.Element, mapping: dict) -> None:
    print("\n[11] EnvironmentalResults — building from scratch...")
    er_sml = find_by_id(sme_root, "EnvironmentalResults")
    if er_sml is None:
        print("    [ERROR] EnvironmentalResults SML not found")
        return

    impacts = mapping.get("impacts", {}).get("EF 3.0", {})
    out_flows = mapping.get("output_flows", {})

    # Remove existing value element (empty in template)
    old_val = er_sml.find(T("value"))
    if old_val is not None:
        er_sml.remove(old_val)
    er_val = ET.SubElement(er_sml, T("value"))

    total_sv = 0

    # Load registry
    registry_yaml_path = os.path.join(REPO_ROOT, "docs", "model", "environmental-indicator-registry.yaml")
    ind_map = {}
    try:
        # We will parse yaml manually for safety if yaml not found
        import yaml
        with open(registry_yaml_path, 'r', encoding='utf-8') as f:
            registry_data = yaml.safe_load(f)
        for ind in registry_data.get("indicators", []):
            ind_map[ind["indicatorCode"]] = ind
    except Exception as e:
        print(f"    [WARN] Could not load registry YAML properly: {e}")

    def _get_registry_info(code, fallback_unit):
        rec = ind_map.get(code, {})
        u = rec.get("characterizationUnit", fallback_unit)
        uid = rec.get("characterizationUnitId", "https://wg-epd.example.com/draft/v1/Value/Unit_" + u.replace(' ', '_'))
        bu = rec.get("baseUnit", "")
        buid = rec.get("baseUnitId", "https://wg-epd.example.com/draft/v1/Value/Unit_" + bu.replace(' ', '_')) if bu else ""
        return uid, bu, buid

    # --- Impact indicators from source ---
    for epd_key, id_short, ind_code, cat, unit, name in IMPACT_INDICATORS:
        src = impacts.get(epd_key)
        if src is not None:
            svs = build_stage_values_from_source(src)
        else:
            svs = build_illustrative_stage_values(_default_illustrative_stages())
        uid, bu, buid = _get_registry_info(ind_code, unit)
        smc = build_environmental_result_smc(id_short, cat, ind_code, name, unit, uid, bu, buid, svs)
        er_val.append(smc)
        total_sv += len(svs)
        print("    [source]      " + id_short + "  (" + str(len(svs)) + " stages)")

    # --- Illustrative impact indicators ---
    ill_stages = build_illustrative_stage_values(_default_illustrative_stages())
    for id_short, ind_code, cat, unit, name in ILLUSTRATIVE_INDICATORS:
        svs = build_illustrative_stage_values(_default_illustrative_stages())
        uid, bu, buid = _get_registry_info(ind_code, unit)
        smc = build_environmental_result_smc(id_short, cat, ind_code, name, unit, uid, bu, buid, svs)
        er_val.append(smc)
        total_sv += len(svs)
        print("    [illustrative] " + id_short + "  (" + str(len(svs)) + " stages)")

    # --- Output flows from source ---
    for epd_key, id_short, ind_code, cat, unit, name in OUTPUT_FLOW_INDICATORS:
        src = out_flows.get(epd_key)
        if src is not None:
            svs = build_stage_values_from_source(src)
        else:
            svs = build_illustrative_stage_values(_default_illustrative_stages())
        uid, bu, buid = _get_registry_info(ind_code, unit)
        smc = build_environmental_result_smc(id_short, cat, ind_code, name, unit, uid, bu, buid, svs)
        er_val.append(smc)
        total_sv += len(svs)
        print("    [source]      " + id_short + "  (" + str(len(svs)) + " stages)")

    # --- Illustrative ResourceUse ---
    for id_short, ind_code, cat, unit, name, stages in ILLUSTRATIVE_RESOURCE_USE:
        svs = build_illustrative_stage_values(stages)
        uid, bu, buid = _get_registry_info(ind_code, unit)
        smc = build_environmental_result_smc(id_short, cat, ind_code, name, unit, uid, bu, buid, svs)
        er_val.append(smc)
        total_sv += len(svs)
        print("    [illustrative] " + id_short + "  (" + str(len(svs)) + " stages) [ResourceUse]")

    total_er = len(list(er_val))
    print("    Total EnvironmentalResult entries: " + str(total_er))
    print("    Total StageValue entries:          " + str(total_sv))


# ---------------------------------------------------------------------------
# AASX packaging
# ---------------------------------------------------------------------------

def package_aasx(xml_bytes: bytes, image_path: str, output_path: str, pdf_path: str = None) -> None:
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    content_types = (
        '<?xml version="1.0" encoding="utf-8"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Default Extension="jpg" ContentType="image/jpeg"/>'
        '<Default Extension="pdf" ContentType="application/pdf"/>'
        '<Override PartName="/aasx/aasx-origin"'
        ' ContentType="application/vnd.openxmlformats-openSourceAutomationSystem.aasx+zip"/>'
        '</Types>'
    )
    rels = (
        '<?xml version="1.0" encoding="utf-8"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Type="http://www.admin-shell.io/aasx/relationships/aasx-origin"'
        ' Target="/aasx/aasx-origin" Id="r1"/>'
        '</Relationships>'
    )
    origin_rels = (
        '<?xml version="1.0" encoding="utf-8"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Type="http://www.admin-shell.io/aasx/relationships/aas-spec"'
        ' Target="/aasx/data.xml" Id="r1"/>'
        '</Relationships>'
    )

    with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED) as zout:
        zout.writestr("[Content_Types].xml", content_types)
        zout.writestr("_rels/.rels", rels)
        zout.writestr("aasx/aasx-origin", b"")
        zout.writestr("aasx/_rels/aasx-origin.rels", origin_rels)
        zout.writestr("aasx/data.xml", xml_bytes)

        if os.path.isfile(image_path):
            with open(image_path, "rb") as f:
                img_bytes = f.read()
            zip_img = IMAGE_AASX_PATH.lstrip("/")
            zout.writestr(zip_img, img_bytes)
            print("    Packaged image: " + zip_img + " (" + str(len(img_bytes)) + " bytes)")
        else:
            print("    [WARN] Product image not found: " + image_path)
            
        if pdf_path and os.path.isfile(pdf_path):
            with open(pdf_path, "rb") as f:
                pdf_bytes = f.read()
            zip_pdf = "aasx/files/" + os.path.basename(pdf_path)
            zout.writestr(zip_pdf, pdf_bytes)
            print("    Packaged PDF: " + zip_pdf + " (" + str(len(pdf_bytes)) + " bytes)")
        else:
            print("    [WARN] EPD Document PDF not found: " + str(pdf_path))


# ---------------------------------------------------------------------------
# Validation checks
# ---------------------------------------------------------------------------

def validate(output_path: str) -> None:
    print("\n[VALIDATION]")
    with zipfile.ZipFile(output_path, "r") as z:
        entries = z.namelist()
        print("  AASX entries: " + str(entries))

        img_entry = IMAGE_AASX_PATH.lstrip("/")
        if img_entry in entries:
            print("  PASS  product image at " + img_entry)
        else:
            print("  FAIL  product image missing")
            
        pdf_entry = "aasx/files/wago-00001-v01-01-en.pdf"
        if pdf_entry in entries:
            # Check size > 0
            size = z.getinfo(pdf_entry).file_size
            if size > 0:
                print("  PASS  epdDocument PDF at " + pdf_entry + " (" + str(size) + " bytes)")
            else:
                print("  FAIL  epdDocument PDF is empty")
        else:
            print("  FAIL  epdDocument PDF missing")

        xml_bytes = z.read("aasx/data.xml")

    tree = ET.parse(io.BytesIO(xml_bytes))
    root = tree.getroot()

    # Check no legacy declaredUnit SMC
    legacy = [
        el for el in root.iter(T("submodelElementCollection"))
        if (el.find(T("idShort")) is not None
            and el.find(T("idShort")).text == "declaredUnit"
            and el.find(T("semanticId") + "/" + T("keys") + "/" + T("key") + "/" + T("value")) is not None
            and el.find(T("semanticId") + "/" + T("keys") + "/" + T("key") + "/" + T("value")).text
            == LEGACY_DECLARED_UNIT_SEM)
    ]
    if legacy:
        print("  FAIL  " + str(len(legacy)) + " legacy declaredUnit SMC(s) remain")
    else:
        print("  PASS  no legacy declaredUnit SMC")

    # Count StageValues
    sv_count = sum(
        1 for el in root.iter(T("submodelElementCollection"))
        if (el.find(T("idShort")) is not None
            and el.find(T("idShort")).text is not None
            and el.find(T("idShort")).text.startswith("sv_"))
    )
    print("  INFO  StageValue SMCs in output: " + str(sv_count))

    # Count EnvironmentalResult entries
    er_count = 0
    for el in root.iter(T("submodelElementList")):
        id_el = el.find(T("idShort"))
        if id_el is not None and id_el.text == "EnvironmentalResults":
            val = el.find(T("value"))
            er_count = len(list(val)) if val is not None else 0
    print("  INFO  EnvironmentalResult entries: " + str(er_count))

    # DeclaredUnit (canonical) quantity
    for el in root.iter(T("submodelElementCollection")):
        id_el = el.find(T("idShort"))
        if id_el is not None and id_el.text == "DeclaredUnit":
            val = el.find(T("value"))
            if val is not None:
                qty_el = find_by_id(val, "quantity")
                unit_el = find_by_id(val, "unit")
                qty_v = qty_el.find(T("value")) if qty_el is not None else None
                unit_v = unit_el.find(T("value")) if unit_el is not None else None
                print("  INFO  DeclaredUnit: quantity=" +
                      (qty_v.text if qty_v is not None else "?") +
                      "  unit=" + (unit_v.text if unit_v is not None else "?"))
            break

    # productImage value
    for el in root.iter(T("file")):
        id_el = el.find(T("idShort"))
        if id_el is not None and id_el.text == "productImage":
            v = el.find(T("value"))
            print("  INFO  productImage value = " + (v.text if v is not None else "empty"))
            break


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _is_numeric(s: Optional[str]) -> bool:
    if not s:
        return False
    try:
        float(s)
        return True
    except (ValueError, TypeError):
        return False


def populate_lca_standards_pcr(sme_root: ET.Element) -> None:
    print("\n[6] lca_StandardsPcr...")
    lsp = find_by_id(sme_root, "lca_StandardsPcr")
    if lsp is None:
        print("    [WARN] not found")
        return
    v = get_val(lsp)

    # standardsCompliance
    sc = find_by_id(v, "standardsCompliance")
    if sc is not None:
        sc_val = sc.find(T("value"))
        if sc_val is not None and len(list(sc_val)) == 0:
            sc_val.text = None
            for i, std in enumerate(["ISO 14025", "EN 15804"]):
                prop = ET.SubElement(sc_val, T("property"))
                ET.SubElement(prop, T("idShort")).text = str(i)
                ET.SubElement(prop, T("valueType")).text = "xs:string"
                ET.SubElement(prop, T("value")).text = std

    # productCategoryRules
    pcr = find_by_id(v, "productCategoryRules")
    if pcr is not None:
        pcr_val = pcr.find(T("value"))
        if pcr_val is not None and len(list(pcr_val)) == 0:
            pcr_val.text = None
            for i, rule in enumerate(["PCR-ed4-EN-2021 09 06", "PEP-PCR-ed3-EN-2015 04 02"]):
                prop = ET.SubElement(pcr_val, T("property"))
                ET.SubElement(prop, T("idShort")).text = str(i)
                ET.SubElement(prop, T("valueType")).text = "xs:string"
                ET.SubElement(prop, T("value")).text = rule
    print("    OK")

def populate_epd_document(sme_root: ET.Element) -> None:
    print("\n[12] epdDocument...")
    doc = find_by_id(sme_root, "epdDocument")
    if doc is not None:
        v = doc.find(T("value"))
        if v is None:
            v = ET.SubElement(doc, T("value"))
        v.text = "/aasx/files/wago-00001-v01-01-en.pdf"
        
        ct = doc.find(T("contentType"))
        if ct is None:
            ct = ET.SubElement(doc, T("contentType"))
        ct.text = "application/pdf"
        print("    OK")
    else:
        print("    [WARN] epdDocument not found")

# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    print("=" * 70)
    print("WAGO EPD AAS Instance Generator")
    print("=" * 70)

    print("\nLoading mapping JSON...")
    with open(MAPPING_JSON, "r", encoding="utf-8") as f:
        mapping = json.load(f)

    print("Loading template AASX...")
    with zipfile.ZipFile(TEMPLATE_AASX, "r") as z:
        data_xml_bytes = z.read("aasx/data.xml")

    tree = ET.parse(io.BytesIO(data_xml_bytes))
    root = tree.getroot()

    # Update submodel ID for the instance
    sm_el = root.find(".//" + T("submodel"))
    if sm_el is not None:
        id_el = sm_el.find(T("id"))
        if id_el is not None:
            id_el.text = "https://wago.com/aas/submodel/EPDTypeIII/WAGO-221-422-v01.01"
        dn_el = sm_el.find(".//" + T("langStringNameType") + "/" + T("text"))
        if dn_el is not None:
            dn_el.text = "WAGO 221-422 EPD Type III Submodel"

    # Update AAS ID and Submodel Reference
    aas_el = root.find(".//" + T("assetAdministrationShell"))
    if aas_el is not None:
        aas_id = aas_el.find(T("id"))
        if aas_id is not None:
            aas_id.text = "https://wago.com/aas/EPDTypeIII/WAGO-221-422-v01.01"
        
        asset_info = aas_el.find(".//" + T("assetInformation"))
        if asset_info is not None:
            asset_kind = asset_info.find(T("assetKind"))
            if asset_kind is not None:
                asset_kind.text = "Instance"
            global_asset_id = asset_info.find(T("globalAssetId"))
            if global_asset_id is not None:
                global_asset_id.text = "https://wago.com/asset/EPDTypeIII/WAGO-221-422"

        submodel_ref_value = aas_el.find(".//" + T("submodels") + "//" + T("reference") + "//" + T("keys") + "//" + T("key") + "//" + T("value"))
        if submodel_ref_value is not None:
            submodel_ref_value.text = "https://wago.com/aas/submodel/EPDTypeIII/WAGO-221-422-v01.01"

    sme_root = sm_el.find(T("submodelElements"))
    cd_root = root.find(".//" + T("conceptDescriptions"))

    # Run all population steps
    remove_legacy(sme_root, cd_root)
    populate_identification_publication(sme_root)
    populate_program_operator_verification(sme_root)
    populate_manufacturer_product(sme_root, mapping)
    populate_lca_methodology(sme_root)
    populate_lca_standards_pcr(sme_root)
    populate_canonical_declared_unit(sme_root, mapping)
    populate_functional_unit(sme_root)
    populate_epd_scope(sme_root)
    populate_content_declaration(sme_root, mapping)
    populate_environmental_results(sme_root, mapping)
    populate_epd_document(sme_root)

    # Serialise
    ET.indent(tree, space="  ")
    buf = io.BytesIO()
    tree.write(buf, encoding="utf-8", xml_declaration=True)
    patched_xml = buf.getvalue()

    print("\nPackaging AASX: " + OUTPUT_AASX)
    pdf_path = os.path.join(REPO_ROOT, "examples", "wago-00001", "source", "wago-00001-v01-01-en.pdf")
    package_aasx(patched_xml, PRODUCT_IMAGE, OUTPUT_AASX, pdf_path)

    validate(OUTPUT_AASX)
    print("\nDone.")


if __name__ == "__main__":
    main()
