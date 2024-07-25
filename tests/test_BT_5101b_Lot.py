# tests/test_BT_5101b_Lot.py

import pytest
import json
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main

def test_bt_5101b_lot_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:ProcurementProject>
                <cac:RealizedLocation>
                    <cac:Address>
                        <cbc:StreetName>Main Street</cbc:StreetName>
                        <cbc:AdditionalStreetName>Building B1</cbc:AdditionalStreetName>
                        <cac:AddressLine>
                            <cbc:Line>3rd floor</cbc:Line>
                        </cac:AddressLine>
                    </cac:Address>
                </cac:RealizedLocation>
            </cac:ProcurementProject>
        </cac:ProcurementProjectLot>
    </root>
    """
    xml_file = tmp_path / "test_input_lot_place_performance_streetline1.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open('output.json', 'r') as f:
        result = json.load(f)

    assert "tender" in result
    assert "items" in result["tender"]
    assert len(result["tender"]["items"]) == 1
    item = result["tender"]["items"][0]
    assert item["relatedLot"] == "LOT-0001"
    assert "deliveryAddresses" in item
    assert len(item["deliveryAddresses"]) == 1
    address = item["deliveryAddresses"][0]
    assert "streetAddress" in address
    assert address["streetAddress"] == "Main Street, Building B1, 3rd floor"

if __name__ == "__main__":
    pytest.main()