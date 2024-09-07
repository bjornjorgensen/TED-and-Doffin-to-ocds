# tests/test_BT_503_UBO.py

import pytest
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main


def test_bt_503_ubo_integration(tmp_path):
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
                                <cac:Contact>
                                    <cbc:Telephone>+123 4567890</cbc:Telephone>
                                </cac:Contact>
                            </efac:UltimateBeneficialOwner>
                        </efac:Organizations>
                    </efext:EformsExtension>
                </ext:ExtensionContent>
            </ext:UBLExtension>
        </ext:UBLExtensions>
    </root>
    """
    xml_file = tmp_path / "test_input_ubo_telephone.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open("output.json", "r") as f:
        result = json.load(f)

    assert "parties" in result, "Expected 'parties' in result"
    assert (
        len(result["parties"]) == 1
    ), f"Expected 1 party, got {len(result['parties'])}"

    party = result["parties"][0]
    assert party["id"] == "ORG-0001", f"Expected party id 'ORG-0001', got {party['id']}"
    assert "beneficialOwners" in party, "Expected 'beneficialOwners' in party"
    assert (
        len(party["beneficialOwners"]) == 1
    ), f"Expected 1 beneficial owner, got {len(party['beneficialOwners'])}"

    ubo = party["beneficialOwners"][0]
    assert ubo["id"] == "UBO-0001", f"Expected UBO id 'UBO-0001', got {ubo['id']}"
    assert (
        ubo["telephone"] == "+123 4567890"
    ), f"Expected telephone '+123 4567890', got {ubo['telephone']}"


if __name__ == "__main__":
    pytest.main()
