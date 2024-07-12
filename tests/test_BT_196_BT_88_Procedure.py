# tests/test_BT_196_BT_88_Procedure.py

import pytest
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main

def test_bt_196_bt_88_procedure_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
          xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
          xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1">
        <cac:TenderingProcess>
            <ext:UBLExtensions>
                <ext:UBLExtension>
                    <ext:ExtensionContent>
                        <efext:EformsExtension>
                            <efac:FieldsPrivacy>
                                <efbc:FieldIdentifierCode>pro-fea</efbc:FieldIdentifierCode>
                                <efbc:ReasonDescription>Information delayed publication due to strategic considerations</efbc:ReasonDescription>
                            </efac:FieldsPrivacy>
                        </efext:EformsExtension>
                    </ext:ExtensionContent>
                </ext:UBLExtension>
            </ext:UBLExtensions>
        </cac:TenderingProcess>
    </root>
    """
    xml_file = tmp_path / "test_input_bt_196_bt_88_procedure.xml"
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
    expected_rationale = "Information delayed publication due to strategic considerations"
    assert withheld_info["rationale"] == expected_rationale, f"Expected rationale '{expected_rationale}', got {withheld_info['rationale']}"
    assert withheld_info["id"] == "pro-fea-1", f"Expected id 'pro-fea-1', got {withheld_info['id']}"
    assert withheld_info["field"] == "pro-fea", f"Expected field 'pro-fea', got {withheld_info['field']}"
    assert withheld_info["name"] == "Procedure Features Justification", f"Expected name 'Procedure Features Justification', got {withheld_info['name']}"

if __name__ == "__main__":
    pytest.main()