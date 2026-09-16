import os
import sys

# Ensure scripts directory is in path
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(REPO_ROOT, "scripts"))

from patch_template_aasx import patch, TEMPLATE_AASX
from patch_template_cds import patch_template

def main():
    print("Applying structural patches to canonical template AASX...")
    patch(TEMPLATE_AASX)
    print("\nApplying semantic patches to canonical template AASX (ConceptDescriptions)...")
    patch_template()
    print("\nCanonical template fully patched!")

if __name__ == "__main__":
    main()
