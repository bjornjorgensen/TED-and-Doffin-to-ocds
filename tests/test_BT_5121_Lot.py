# tests/test_BT_5121_Lot.py

import pytest
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main

def test_bt_5121_lot_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:ProcurementProject>
                <cac:RealizedLocation>
                    <cac:Address>
                        <cbc:PostalZone>XY14 2LG</cbc:PostalZone>
                    </cac:Address>
                </cac:RealizedLocation>
            </cac:ProcurementProject>
        </cac:ProcurementProjectLot>
    </root>
    """
    xml_file = tmp_path / "test_input_bt_5121_lot.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open('output.json', 'r') as f:
        result = json.load(f)

    assert "tender" in result, "Expected 'tender' in result"
    assert "items" in result["tender"], "Expected 'items' in tender"
    assert len(result["tender"]["items"]) == 1, f"Expected 1 item, got {len(result['tender']['items'])}"

    item = result["tender"]["items"][0]
    assert item["relatedLot"] == "LOT-0001", f"Expected related lot 'LOT-0001', got {item['relatedLot']}"
    assert "deliveryAddresses" in item, "Expected 'deliveryAddresses' in item"
    assert len(item["deliveryAddresses"]) == 1, f"Expected 1 delivery address, got {len(item['deliveryAddresses'])}"
    assert "postalCode" in item["deliveryAddresses"][0], "Expected 'postalCode' in delivery address"
    expected_postal_code = "XY14 2LG"
    assert item["deliveryAddresses"][0]["postalCode"] == expected_postal_code, f"Expected postal code '{expected_postal_code}', got {item['deliveryAddresses'][0]['postalCode']}"

if __name__ == "__main__":
    pytest.main()