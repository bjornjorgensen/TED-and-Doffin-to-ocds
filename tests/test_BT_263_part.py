# tests/test_BT_263_part.py

import pytest
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main

def test_bt_263_part_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Part">PART-0001</cbc:ID>
            <cac:ProcurementProject>
                <cac:AdditionalCommodityClassification>
                    <cbc:ItemClassificationCode listName="cpv">15311200</cbc:ItemClassificationCode>
                </cac:AdditionalCommodityClassification>
            </cac:ProcurementProject>
        </cac:ProcurementProjectLot>
    </root>
    """
    xml_file = tmp_path / "test_input_additional_classification_code_part.xml"
    xml_file.write_text(xml_content)

    result = main(str(xml_file), "ocds-test-prefix")

    assert "tender" in result
    assert "items" in result["tender"]
    assert len(result["tender"]["items"]) == 1
    item = result["tender"]["items"][0]
    assert item["id"] == "1"
    assert "additionalClassifications" in item
    assert len(item["additionalClassifications"]) == 1
    assert item["additionalClassifications"][0]["id"] == "15311200"
    assert item["additionalClassifications"][0]["scheme"] == "CPV"

if __name__ == "__main__":
    pytest.main()