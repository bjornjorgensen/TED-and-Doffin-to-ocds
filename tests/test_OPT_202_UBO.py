# tests/test_OPT_202_UBO.py

import pytest
import json
import os
import sys
import logging

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main

logger = logging.getLogger(__name__)

def test_beneficial_owner_identifier(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
          xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1">
        <ext:UBLExtensions>
            <ext:UBLExtension>
                <ext:ExtensionContent>
                    <efext:EformsExtension>
                        <efac:Organizations>
                            <efac:Organization>
                                <efac:Company>
                                    <cac:PartyIdentification>
                                        <cbc:ID schemeName="organization">ORG-0001</cbc:ID>
                                    </cac:PartyIdentification>
                                </efac:Company>
                            </efac:Organization>
                            <efac:UltimateBeneficialOwner>
                                <cbc:ID schemeName="ubo">UBO-0001</cbc:ID>
                            </efac:UltimateBeneficialOwner>
                        </efac:Organizations>
                    </efext:EformsExtension>
                </ext:ExtensionContent>
            </ext:UBLExtension>
        </ext:UBLExtensions>
    </root>
    """
    xml_file = tmp_path / "test_input_beneficial_owner_identifier.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open('output.json', 'r') as f:
        result = json.load(f)

    logger.info(f"Test result: {json.dumps(result, indent=2)}")

    assert "parties" in result, "parties key not found in result"
    assert len(result["parties"]) == 1, f"Expected 1 party, found {len(result['parties'])}"
    party = result["parties"][0]
    assert party["id"] == "ORG-0001", f"Expected party id 'ORG-0001', found {party['id']}"
    assert "beneficialOwners" in party, "beneficialOwners key not found in party"
    assert len(party["beneficialOwners"]) == 1, f"Expected 1 beneficial owner, found {len(party['beneficialOwners'])}"
    assert party["beneficialOwners"][0]["id"] == "UBO-0001", f"Expected beneficial owner id 'UBO-0001', found {party['beneficialOwners'][0]['id']}"

if __name__ == "__main__":
    pytest.main()