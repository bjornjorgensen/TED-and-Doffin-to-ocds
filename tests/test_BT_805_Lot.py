# tests/test_BT_805_Lot.py

import pytest
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main

def test_bt_805_lot_green_procurement_criteria_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:ProcurementProject>
                <cac:ProcurementAdditionalType>
                    <cbc:ProcurementTypeCode listName="gpp-criteria">eu</cbc:ProcurementTypeCode>
                </cac:ProcurementAdditionalType>
                <cac:ProcurementAdditionalType>
                    <cbc:ProcurementTypeCode listName="gpp-criteria">national</cbc:ProcurementTypeCode>
                </cac:ProcurementAdditionalType>
            </cac:ProcurementProject>
        </cac:ProcurementProjectLot>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0002</cbc:ID>
            <cac:ProcurementProject>
                <cac:ProcurementAdditionalType>
                    <cbc:ProcurementTypeCode listName="gpp-criteria">none</cbc:ProcurementTypeCode>
                </cac:ProcurementAdditionalType>
            </cac:ProcurementProject>
        </cac:ProcurementProjectLot>
    </root>
    """
    xml_file = tmp_path / "test_input_green_procurement_criteria.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open('output.json', 'r') as f:
        result = json.load(f)

    assert "tender" in result
    assert "lots" in result["tender"]
    
    gpp_lots = [lot for lot in result["tender"]["lots"] if "hasSustainability" in lot and lot["hasSustainability"]]
    assert len(gpp_lots) == 1

    lot_1 = gpp_lots[0]
    assert lot_1["id"] == "LOT-0001"
    assert lot_1["hasSustainability"] is True
    assert "sustainability" in lot_1
    assert len(lot_1["sustainability"]) == 2
    assert {"strategies": ["euGPPCriteria"]} in lot_1["sustainability"]
    assert {"strategies": ["nationalGPPCriteria"]} in lot_1["sustainability"]

    lot_2 = next((lot for lot in result["tender"]["lots"] if lot["id"] == "LOT-0002"), None)
    assert lot_2 is not None
    assert "hasSustainability" not in lot_2
    assert "sustainability" not in lot_2

if __name__ == "__main__":
    pytest.main()