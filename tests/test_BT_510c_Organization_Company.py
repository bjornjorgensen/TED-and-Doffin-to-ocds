# tests/test_BT_510c_Organization_Company.py

import pytest
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main

def test_bt_510c_organization_company_integration(tmp_path):
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
                                    <cac:PostalAddress>
                                        <cbc:StreetName>2, rue de Europe</cbc:StreetName>
                                        <cbc:AdditionalStreetName>Building A</cbc:AdditionalStreetName>
                                        <cac:AddressLine>
                                            <cbc:Line>3rd Floor</cbc:Line>
                                        </cac:AddressLine>
                                    </cac:PostalAddress>
                                </efac:Company>
                            </efac:Organization>
                        </efac:Organizations>
                    </efext:EformsExtension>
                </ext:ExtensionContent>
            </ext:UBLExtension>
        </ext:UBLExtensions>
    </root>
    """
    xml_file = tmp_path / "test_input_organization_streetline2.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open('output.json', 'r') as f:
        result = json.load(f)

    assert "parties" in result, "Expected 'parties' in result"
    assert len(result["parties"]) == 1, f"Expected 1 party, got {len(result['parties'])}"

    party = result["parties"][0]
    assert party["id"] == "ORG-0001", f"Expected party id 'ORG-0001', got {party['id']}"
    assert "address" in party, "Expected 'address' in party"
    assert "streetAddress" in party["address"], "Expected 'streetAddress' in party address"
    expected_street_address = "2, rue de Europe, Building A, 3rd Floor"
    assert party["address"]["streetAddress"] == expected_street_address, f"Expected street address '{expected_street_address}', got {party['address']['streetAddress']}"

if __name__ == "__main__":
    pytest.main()