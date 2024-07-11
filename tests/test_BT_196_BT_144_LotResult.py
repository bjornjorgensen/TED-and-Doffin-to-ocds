# tests/test_BT_196_BT_144_LotResult.py

import pytest
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main

def test_bt_196_bt_144_lotresult_integration(tmp_path):
    xml_content = """
    <root xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
          xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
          xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <ext:UBLExtensions>
            <ext:UBLExtension>
                <ext:ExtensionContent>
                    <efext:EformsExtension>
                        <efac:NoticeResult>
                            <efac:LotResult>
                                <cbc:ID>lot-1</cbc:ID>
                                <efac:DecisionReason>
                                    <efac:FieldsPrivacy>
                                        <efbc:FieldIdentifierCode>no-awa-rea</efbc:FieldIdentifierCode>
                                        <efbc:ReasonDescription languageID="ENG">Information delayed publication because of ...</efbc:ReasonDescription>
                                    </efac:FieldsPrivacy>
                                </efac:DecisionReason>
                            </efac:LotResult>
                        </efac:NoticeResult>
                    </efext:EformsExtension>
                </ext:ExtensionContent>
            </ext:UBLExtension>
        </ext:UBLExtensions>
    </root>
    """
    xml_file = tmp_path / "test_input_bt_196_bt_144_lotresult.xml"
    xml_file.write_text(xml_content)

    result = main(str(xml_file), "ocds-test-prefix")

    print(f"Result: {json.dumps(result, indent=2)}")  # Debug print

    assert "withheldInformation" in result, "withheldInformation not found in result"
    assert len(result["withheldInformation"]) > 0, "No withheld information items found"
    
    no_awa_rea_item = next((item for item in result["withheldInformation"] if item.get("id") == "no-awa-rea-lot-1"), None)
    assert no_awa_rea_item is not None, "No withheld information item for no award reason found"
    assert "rationale" in no_awa_rea_item, "rationale not found in withheld information item"
    assert no_awa_rea_item["rationale"] == "Information delayed publication because of ...", f"Expected rationale 'Information delayed publication because of ...', got {no_awa_rea_item['rationale']}"

if __name__ == "__main__":
    pytest.main()