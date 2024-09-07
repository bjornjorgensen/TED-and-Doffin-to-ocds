# tests/test_BT_25_Lot.py

import pytest
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main


def test_bt_25_lot_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:ProcurementProject>
                <cbc:EstimatedOverallContractQuantity unitCode="TNE">45000</cbc:EstimatedOverallContractQuantity>
            </cac:ProcurementProject>
        </cac:ProcurementProjectLot>
    </root>
    """
    xml_file = tmp_path / "test_input_lot_quantity.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open("output.json", "r") as f:
        result = json.load(f)

    assert "tender" in result, "Expected 'tender' in result"
    assert "items" in result["tender"], "Expected 'items' in tender"
    assert (
        len(result["tender"]["items"]) == 1
    ), f"Expected 1 item, got {len(result['tender']['items'])}"

    item = result["tender"]["items"][0]
    assert item["id"] == "1", f"Expected item id '1', got {item['id']}"
    assert item["quantity"] == 45000, f"Expected quantity 45000, got {item['quantity']}"
    assert (
        item["relatedLot"] == "LOT-0001"
    ), f"Expected relatedLot 'LOT-0001', got {item['relatedLot']}"
    assert (
        item["unit"]["id"] == "TNE"
    ), f"Expected unit id 'TNE', got {item['unit']['id']}"


if __name__ == "__main__":
    pytest.main()
