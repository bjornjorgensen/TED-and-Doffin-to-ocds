# tests/test_BT_195_BT_163_Tender.py

import pytest
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main

def test_bt_195_bt_163_unpublished_concession_value_description_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
          xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
          xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1">
        <ext:UBLExtensions>
            <ext:UBLExtension>
                <ext:ExtensionContent>
                    <efext:EformsExtension>
                        <efac:NoticeResult>
                            <efac:LotTender>
                                <cbc:ID schemeName="result">TEN-0001</cbc:ID>
                                <efac:ConcessionRevenue>
                                    <efac:FieldsPrivacy>
                                        <efbc:FieldIdentifierCode listName="non-publication-identifier">val-con-des</efbc:FieldIdentifierCode>
                                    </efac:FieldsPrivacy>
                                </efac:ConcessionRevenue>
                            </efac:LotTender>
                        </efac:NoticeResult>
                    </efext:EformsExtension>
                </ext:ExtensionContent>
            </ext:UBLExtension>
        </ext:UBLExtensions>
    </root>
    """
    xml_file = tmp_path / "test_input_unpublished_concession_value_description.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open('output.json', 'r') as f:
        result = json.load(f)

    assert "withheldInformation" in result, "Expected 'withheldInformation' in result"
    assert len(result["withheldInformation"]) == 1, f"Expected 1 withheld information item, got {len(result['withheldInformation'])}"

    withheld_info = result["withheldInformation"][0]
    assert withheld_info["id"] == "val-con-des-TEN-0001", f"Expected id 'val-con-des-TEN-0001', got {withheld_info['id']}"
    assert withheld_info["field"] == "val-con-des", f"Expected field 'val-con-des', got {withheld_info['field']}"
    assert withheld_info["name"] == "Concession Value Description", f"Expected name 'Concession Value Description', got {withheld_info['name']}"

if __name__ == "__main__":
    pytest.main()