# tests/test_BT_196_BT_773_Tender.py

import pytest
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main

def test_bt_196_bt_773_tender_integration(tmp_path):
    xml_content = """
    <root xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
          xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
          xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1">
        <ext:UBLExtensions>
            <ext:UBLExtension>
                <ext:ExtensionContent>
                    <efext:EformsExtension>
                        <efac:NoticeResult>
                            <efac:LotTender>
                                <efbc:ID>Tender1</efbc:ID>
                                <efac:SubcontractingTerm>
                                    <efbc:TermCode listName="applicability">code</efbc:TermCode>
                                    <efac:FieldsPrivacy>
                                        <efbc:FieldIdentifierCode>sub-con</efbc:FieldIdentifierCode>
                                        <efbc:ReasonDescription>Information delayed publication due to ongoing negotiations</efbc:ReasonDescription>
                                    </efac:FieldsPrivacy>
                                </efac:SubcontractingTerm>
                            </efac:LotTender>
                        </efac:NoticeResult>
                    </efext:EformsExtension>
                </ext:ExtensionContent>
            </ext:UBLExtension>
        </ext:UBLExtensions>
    </root>
    """
    xml_file = tmp_path / "test_input_bt_196_bt_773_tender.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open('output.json', 'r') as f:
        result = json.load(f)

    assert "withheldInformation" in result, "Expected 'withheldInformation' in result"
    assert len(result["withheldInformation"]) == 1, f"Expected 1 withheld information item, got {len(result['withheldInformation'])}"

    withheld_info = result["withheldInformation"][0]
    assert "rationale" in withheld_info, "Expected 'rationale' in withheld information"
    assert "id" in withheld_info, "Expected 'id' in withheld information"
    assert "field" in withheld_info, "Expected 'field' in withheld information"
    assert "name" in withheld_info, "Expected 'name' in withheld information"
    expected_rationale = "Information delayed publication due to ongoing negotiations"
    assert withheld_info["rationale"] == expected_rationale, f"Expected rationale '{expected_rationale}', got {withheld_info['rationale']}"
    assert withheld_info["id"] == "sub-con-Tender1", f"Expected id 'sub-con-Tender1', got {withheld_info['id']}"
    assert withheld_info["field"] == "sub-con", f"Expected field 'sub-con', got {withheld_info['field']}"
    assert withheld_info["name"] == "Subcontracting Justification", f"Expected name 'Subcontracting Justification', got {withheld_info['name']}"

if __name__ == "__main__":
    pytest.main()