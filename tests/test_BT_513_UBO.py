# tests/test_BT_513_UBO.py

import pytest
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main


def test_bt_513_ubo_integration(tmp_path):
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
                                <cac:ResidenceAddress>
                                    <cbc:CityName>MouseTown</cbc:CityName>
                                </cac:ResidenceAddress>
                            </efac:UltimateBeneficialOwner>
                        </efac:Organizations>
                    </efext:EformsExtension>
                </ext:ExtensionContent>
            </ext:UBLExtension>
        </ext:UBLExtensions>
    </root>
    """
    xml_file = tmp_path / "test_input_bt_513_ubo.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open("output.json") as f:
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

    bo = party["beneficialOwners"][0]
    assert (
        bo["id"] == "UBO-0001"
    ), f"Expected beneficial owner id 'UBO-0001', got {bo['id']}"
    assert "address" in bo, "Expected 'address' in beneficial owner"
    assert (
        "locality" in bo["address"]
    ), "Expected 'locality' in beneficial owner address"
    expected_locality = "MouseTown"
    assert (
        bo["address"]["locality"] == expected_locality
    ), f"Expected locality '{expected_locality}', got {bo['address']['locality']}"


if __name__ == "__main__":
    pytest.main()
