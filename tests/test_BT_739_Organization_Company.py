# tests/test_BT_739_Organization_Company.py

import pytest
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main

def test_bt_739_organization_company_integration(tmp_path):
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
                                        <cbc:ID schemeName="organization">ORG-0003</cbc:ID>
                                    </cac:PartyIdentification>
                                    <cac:Contact>
                                        <cbc:Telefax>(+33) 2 34 56 78 91</cbc:Telefax>
                                    </cac:Contact>
                                </efac:Company>
                            </efac:Organization>
                        </efac:Organizations>
                    </efext:EformsExtension>
                </ext:ExtensionContent>
            </ext:UBLExtension>
        </ext:UBLExtensions>
    </root>
    """
    xml_file = tmp_path / "test_input_organization_contact_fax.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open('output.json', 'r') as f:
        result = json.load(f)

    assert "parties" in result, "Expected 'parties' in result"
    assert len(result["parties"]) == 1, f"Expected 1 party, got {len(result['parties'])}"

    party = result["parties"][0]
    assert party["id"] == "ORG-0003", f"Expected party id 'ORG-0003', got {party['id']}"
    assert "contactPoint" in party, "Expected 'contactPoint' in party"
    assert "faxNumber" in party["contactPoint"], "Expected 'faxNumber' in contactPoint"
    assert party["contactPoint"]["faxNumber"] == "(+33) 2 34 56 78 91", \
        f"Expected faxNumber '(+33) 2 34 56 78 91', got {party['contactPoint']['faxNumber']}"

if __name__ == "__main__":
    pytest.main()