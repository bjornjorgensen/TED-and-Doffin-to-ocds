# tests/test_BT_196_BT_635_LotResult.py

import pytest
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main

def test_bt_196_bt_635_lotresult_integration(tmp_path):
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
                                <efac:AppealRequestsStatistics>
                                    <efbc:StatisticsCode listName="irregularity-type">irregularity</efbc:StatisticsCode>
                                    <efac:FieldsPrivacy>
                                        <efbc:FieldIdentifierCode>buy-rev-cou</efbc:FieldIdentifierCode>
                                        <efbc:ReasonDescription languageID="ENG">Information delayed publication because of ...</efbc:ReasonDescription>
                                    </efac:FieldsPrivacy>
                                </efac:AppealRequestsStatistics>
                            </efac:LotResult>
                        </efac:NoticeResult>
                    </efext:EformsExtension>
                </ext:ExtensionContent>
            </ext:UBLExtension>
        </ext:UBLExtensions>
    </root>
    """
    xml_file = tmp_path / "test_input_bt_196_bt_635_lotresult.xml"
    xml_file.write_text(xml_content)

    result = main(str(xml_file), "ocds-test-prefix")

    print(f"Result: {json.dumps(result, indent=2)}")  # Debug print

    assert "withheldInformation" in result, "withheldInformation not found in result"
    assert len(result["withheldInformation"]) > 0, "No withheld information items found"
    
    buy_rev_cou_item = next((item for item in result["withheldInformation"] if item.get("id") == "buy-rev-cou-lot-1"), None)
    assert buy_rev_cou_item is not None, "No withheld information item for buyer review count (LotResult) found"
    assert "rationale" in buy_rev_cou_item, "rationale not found in withheld information item"
    assert buy_rev_cou_item["rationale"] == "Information delayed publication because of ...", f"Expected rationale 'Information delayed publication because of ...', got {buy_rev_cou_item['rationale']}"

if __name__ == "__main__":
    pytest.main()