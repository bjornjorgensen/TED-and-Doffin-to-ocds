# tests/test_BT_195_BT_710_LotResult.py

import pytest
import json
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main

def test_bt_195_bt_710_lotresult_integration(tmp_path):
    xml_content = """
    <root xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
          xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
          xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1">
        <ext:UBLExtensions>
            <ext:UBLExtension>
                <ext:ExtensionContent>
                    <efext:EformsExtension>
                        <efac:NoticeResult>
                            <efac:LotResult>
                                <efac:FieldsPrivacy>
                                    <efbc:FieldIdentifierCode>ten-val-low</efbc:FieldIdentifierCode>
                                </efac:FieldsPrivacy>
                                <cbc:ID schemeName="result">RES-0001</cbc:ID>
                            </efac:LotResult>
                        </efac:NoticeResult>
                    </efext:EformsExtension>
                </ext:ExtensionContent>
            </ext:UBLExtension>
        </ext:UBLExtensions>
    </root>
    """
    xml_file = tmp_path / "test_input_unpublished_tender_lowest_value.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open('output.json', 'r') as f:
        result = json.load(f)

    assert "withheldInformation" in result, "Expected 'withheldInformation' in result"
    assert len(result["withheldInformation"]) == 1, f"Expected 1 withheld information item, got {len(result['withheldInformation'])}"

    withheld_item = result["withheldInformation"][0]
    assert withheld_item["id"] == "ten-val-low-RES-0001", f"Expected id 'ten-val-low-RES-0001', got {withheld_item['id']}"
    assert withheld_item["field"] == "ten-val-low", f"Expected field 'ten-val-low', got {withheld_item['field']}"
    assert withheld_item["name"] == "Tender Lowest Value", f"Expected name 'Tender Lowest Value', got {withheld_item['name']}"

if __name__ == "__main__":
    pytest.main()