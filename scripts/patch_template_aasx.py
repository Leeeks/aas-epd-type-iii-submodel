"""
patch_template_aasx.py
======================
Removes the legacy ``declaredUnit`` SMC and its associated ConceptDescriptions
from the EPD Type III template AASX.

Background
----------
The original template contains two representations of the declared unit concept:

  A) Legacy (top-level SMC, idShort = ``declaredUnit``, camelCase,
     semId = https://admin-shell.io/idta/EPD/DeclaredUnit/1/0)
     with children: declaredQuantity / unitOfMeasure / massPerDeclaredUnit
     / referenceServiceLife

  B) Canonical (idShort = ``DeclaredUnit``, PascalCase,
     semId = https://wg-epd.example.com/draft/v1/DeclaredUnit)
     with children: quantity / unit / description

This script removes A) and the orphaned ConceptDescriptions that only
served A).  B) and all other elements are left untouched.

Usage
-----
    conda run -n aas_env python scripts/patch_template_aasx.py

Outputs
-------
  Overwrites  model/template/epd-type-iii-submodel-template.aasx  in-place.
  Prints a change summary to stdout.
"""

import io
import os
import zipfile
import xml.etree.ElementTree as ET
from typing import Optional

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_AASX = os.path.join(REPO_ROOT, "model", "template",
                              "epd-type-iii-submodel-template.aasx")

NS_URI = "https://admin-shell.io/aas/3/0"
NS = {"aas": NS_URI}
ET.register_namespace("aas", NS_URI)

LEGACY_IDSHORT = "declaredUnit"
LEGACY_SEM_ID  = "https://admin-shell.io/idta/EPD/DeclaredUnit/1/0"


def _tag(local: str) -> str:
    return f"{{{NS_URI}}}{local}"

def find_by_id(container: ET.Element, id_short: str) -> Optional[ET.Element]:
    for child in container:
        id_el = child.find(_tag("idShort"))
        if id_el is not None and id_el.text == id_short:
            return child
    return None

def remove_legacy_declared_unit(sme_root: ET.Element) -> int:
    """Remove the top-level legacy ``declaredUnit`` SMC."""
    for child in list(sme_root):
        id_short_el = child.find(_tag("idShort"))
        if id_short_el is None:
            continue
        if id_short_el.text != LEGACY_IDSHORT:
            continue
        sem_el = child.find(
            f"{_tag('semanticId')}/{_tag('keys')}/{_tag('key')}/{_tag('value')}"
        )
        if sem_el is not None and sem_el.text == LEGACY_SEM_ID:
            sme_root.remove(child)
            print(f"  [REMOVED] top-level SMC idShort='{LEGACY_IDSHORT}' "
                  f"(semId={LEGACY_SEM_ID})")
            return 1
    return 0


def remove_legacy_cds(cd_root: ET.Element) -> int:
    """Remove ConceptDescriptions whose ID is in legacy_cds."""
    legacy_cds = {
        "https://admin-shell.io/idta/EPD/DeclaredUnit/1/0",
        "http://eclass.example.com/declaredUnit.qty",
        "http://eclass.example.com/declaredUnit.unit",
        "http://eclass.example.com/kgPerDeclaredUnit.qty",
        "http://eclass.example.com/kgCPerDeclaredUnit.qty",
        "http://eclass.example.com/kgCBiogenicPerDeclaredUnit.qty",
        "http://eclass.example.com/flowDiagramSource",
        "http://eclass.example.com/pictogramSource",
        "http://eclass.example.com/referenceFlow.id",
        "http://eclass.example.com/referenceFlow.amount",
        "https://admin-shell.io/idta/EPD/VerificationStatementUrl/1/0",
        "http://eclass.example.com/dataSetValidUntil",
        "http://eclass.example.com/technicalPurpose",
    }
    removed = 0
    for cd in list(cd_root):
        id_el = cd.find(_tag("id"))
        if id_el is not None and id_el.text in legacy_cds:
            cd_root.remove(cd)
            print(f"  [REMOVED CD] {id_el.text}")
            removed += 1
    return removed


def also_remove_from_manufacturer_product(sme_root: ET.Element) -> int:
    mp = find_by_id(sme_root, "manufacturerProduct")
    if mp is None: return 0
    mp_val = mp.find(_tag("value"))
    if mp_val is None: return 0

    removed = 0
    for child in list(mp_val):
        id_el = child.find(_tag("idShort"))
        if id_el is not None and id_el.text == LEGACY_IDSHORT:
            sem_el = child.find(f"{_tag('semanticId')}/{_tag('keys')}/{_tag('key')}/{_tag('value')}")
            if sem_el is not None and sem_el.text == LEGACY_SEM_ID:
                mp_val.remove(child)
                print(f"  [REMOVED] manufacturerProduct > SMC idShort='{LEGACY_IDSHORT}'")
                removed += 1
    return removed


def patch_lca_methodology_fields(sme_root: ET.Element) -> int:
    lca = find_by_id(sme_root, "LCAMethodology")
    if lca is None: return 0
    val = lca.find(_tag("value"))
    if val is None: return 0

    removed = 0
    for child in list(val):
        id_el = child.find(_tag("idShort"))
        if id_el is not None:
            if id_el.text in ("referenceFlow.id", "referenceFlow.amount", "pictogramSource", "flowDiagramSource", "dataSetValidUntil", "technicalPurpose"):
                val.remove(child)
                print(f"  [REMOVED] LCAMethodology > {id_el.text}")
                removed += 1
            elif id_el.text == "referenceYear":
                id_el.text = "lcaReferenceYear"
                print(f"  [RENAMED] LCAMethodology > referenceYear -> lcaReferenceYear")
            elif id_el.text == "location":
                id_el.text = "geographicalScope"
                print(f"  [RENAMED] LCAMethodology > location -> geographicalScope")
            elif id_el.text == "energyModel":
                id_el.text = "lcaEnergyModel"
                print(f"  [RENAMED] LCAMethodology > energyModel -> lcaEnergyModel")
    return removed


def remove_source_declaration_reference(sme_root: ET.Element) -> int:
    scope = find_by_id(sme_root, "EPDScope")
    if scope is None: return 0
    val = scope.find(_tag("value"))
    if val is None: return 0

    for child in list(val):
        id_el = child.find(_tag("idShort"))
        if id_el is not None and id_el.text == "sourceDeclarationReference":
            val.remove(child)
            print(f"  [REMOVED] EPDScope > sourceDeclarationReference")
            return 1
    return 0


def restructure_biogenic_carbon(sme_root: ET.Element) -> int:
    removed = 0
    mp = find_by_id(sme_root, "manufacturerProduct")
    cd = find_by_id(sme_root, "ContentDeclaration")
    
    if mp is not None and cd is not None:
        mp_val = mp.find(_tag("value"))
        cd_val = cd.find(_tag("value"))
        if mp_val is not None and cd_val is not None:
            # Find SMC biogenicCarbonContent in manufacturerProduct
            bcc = find_by_id(mp_val, "biogenicCarbonContent")
            if bcc is not None:
                mp_val.remove(bcc)
                print("  [MOVED] biogenicCarbonContent from manufacturerProduct to ContentDeclaration")
                cd_val.append(bcc)
                removed += 1

            # Remove flat properties in ContentDeclaration
            for child in list(cd_val):
                id_el = child.find(_tag("idShort"))
                if id_el is not None and id_el.text in ("biogenicCarbonContentProduct", "biogenicCarbonContentPackaging"):
                    cd_val.remove(child)
                    print(f"  [REMOVED] ContentDeclaration > {id_el.text}")
                    removed += 1
    return removed


def clean_identification_publication(sme_root: ET.Element) -> int:
    ip = find_by_id(sme_root, "identificationPublication")
    if ip is None: return 0
    val = ip.find(_tag("value"))
    if val is None: return 0

    removed = 0
    docs = find_by_id(val, "documentIds")
    if docs is not None:
        dval = docs.find(_tag("value"))
        if dval is not None and len(list(dval)) > 0:
            for c in list(dval):
                dval.remove(c)
            print("  [CLEANED] documentIds")
            removed += 1

    langs = find_by_id(val, "languages")
    if langs is not None:
        lval = langs.find(_tag("value"))
        if lval is not None and len(list(lval)) > 0:
            for c in list(lval):
                lval.remove(c)
            print("  [CLEANED] languages")
            removed += 1
    return removed


def remove_verification_statement_url(sme_root: ET.Element) -> int:
    pov = find_by_id(sme_root, "programOperatorVerification")
    if pov is None: return 0
    val = pov.find(_tag("value"))
    if val is None: return 0
    
    tpv = find_by_id(val, "thirdPartyVerifier")
    if tpv is None: return 0
    tval = tpv.find(_tag("value"))
    if tval is None: return 0
    
    removed = 0
    for child in list(tval):
        id_el = child.find(_tag("idShort"))
        if id_el is not None and id_el.text == "verificationStatementUrl":
            tval.remove(child)
            print(f"  [REMOVED] thirdPartyVerifier > verificationStatementUrl")
            removed += 1
    return removed



def patch(aasx_path: str) -> None:
    print(f"\nPatching: {aasx_path}")

    # Read AASX zip
    with zipfile.ZipFile(aasx_path, "r") as z:
        names = z.namelist()
        files: dict[str, bytes] = {n: z.read(n) for n in names}

    data_xml_bytes = files.get("aasx/data.xml")
    if data_xml_bytes is None:
        raise FileNotFoundError("aasx/data.xml not found in AASX package")

    tree = ET.parse(io.BytesIO(data_xml_bytes))
    root = tree.getroot()

    sme_root = root.find(f".//{_tag('submodel')}/{_tag('submodelElements')}")
    if sme_root is None:
        raise RuntimeError("submodelElements not found in data.xml")

    cd_root = root.find(f".//{_tag('conceptDescriptions')}")

    total_removed = 0
    print("\nStep 1: Remove top-level legacy declaredUnit SMC")
    total_removed += remove_legacy_declared_unit(sme_root)

    print("\nStep 2: Remove legacy declaredUnit inside manufacturerProduct")
    total_removed += also_remove_from_manufacturer_product(sme_root)

    print("\nStep 3: Remove legacy ConceptDescriptions")
    if cd_root is not None:
        total_removed += remove_legacy_cds(cd_root)

    print("\nStep 4: Remove legacy LCA Methodology fields")
    rem_lca = patch_lca_methodology_fields(sme_root)
    total_removed += rem_lca

    print("\nStep 5: Remove redundant sourceDeclarationReference from EPDScope")
    total_removed += remove_source_declaration_reference(sme_root)

    print("\nStep 6: Restructure biogenicCarbonContent")
    total_removed += restructure_biogenic_carbon(sme_root)

    print("\nStep 7: Clean identificationPublication fields")
    total_removed += clean_identification_publication(sme_root)
    
    print("\nStep 8: Remove verificationStatementUrl")
    total_removed += remove_verification_statement_url(sme_root)

    print(f"\nTotal elements removed/cleaned: {total_removed}")
    if total_removed == 0:
        print("\nNo changes made — template already clean.")
        return

    # Serialise patched XML
    ET.indent(tree, space="  ")
    buf = io.BytesIO()
    tree.write(buf, encoding="utf-8", xml_declaration=True)
    patched_xml = buf.getvalue()

    # Rewrite AASX zip preserving all other files
    tmp_path = aasx_path + ".tmp"
    with zipfile.ZipFile(tmp_path, "w", compression=zipfile.ZIP_DEFLATED) as zout:
        for name, data in files.items():
            if name == "aasx/data.xml":
                zout.writestr(name, patched_xml)
            else:
                zout.writestr(name, data)

    os.replace(tmp_path, aasx_path)
    print(f"\nDone — {total_removed} change(s) applied. Template saved.")


if __name__ == "__main__":
    patch(TEMPLATE_AASX)
