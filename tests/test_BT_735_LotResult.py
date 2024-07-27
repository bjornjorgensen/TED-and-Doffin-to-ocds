# tests/test_BT_735_LotResult.py

import pytest
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main

def test_bt_735_lotresult_integration(tmp_path):
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
                                <cbc:ID>RES-0001</cbc:ID>
                                <efac:StrategicProcurement>
                                    <efac:StrategicProcurementInformation>
                                        <efbc:ProcurementCategoryCode listName="cvd-contract-type">oth-serv-contr</efbc:ProcurementCategoryCode>
                                    </efac:StrategicProcurementInformation>
                                </efac:StrategicProcurement>
                            </efac:LotResult>
                        </efac:NoticeResult>
                    </efext:EformsExtension>
                </ext:ExtensionContent>
            </ext:UBLExtension>
        </ext:UBLExtensions>
    </root>
    """
    xml_file = tmp_path / "test_input_cvd_contract_type_lotresult.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open('output.json', 'r') as f:
        result = json.load(f)

    assert "awards" in result, "Expected 'awards' in result"
    assert len(result["awards"]) == 1, f"Expected 1 award, got {len(result['awards'])}"

    award = result["awards"][0]
    assert award["id"] == "RES-0001", f"Expected award id 'RES-0001', got {award['id']}"
    assert "items" in award, "Expected 'items' in award"
    assert len(award["items"]) == 1, f"Expected 1 item, got {len(award['items'])}"

    item = award["items"][0]
    assert item["id"] == "1", f"Expected item id '1', got {item['id']}"
    assert "additionalClassifications" in item, "Expected 'additionalClassifications' in item"
    assert len(item["additionalClassifications"]) == 1, f"Expected 1 additional classification, got {len(item['additionalClassifications'])}"

    classification = item["additionalClassifications"][0]
    assert classification["id"] == "oth-serv-contr", f"Expected classification id 'oth-serv-contr', got {classification['id']}"
    assert classification["scheme"] == "eu-cvd-contract-type", f"Expected scheme 'eu-cvd-contract-type', got {classification['scheme']}"
    assert classification["description"] == "Other service contract", f"Expected description 'Other service contract', got {classification['description']}"

if __name__ == "__main__":
    pytest.main()