# tests/test_BT_776_Lot.py

import pytest
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main

def test_bt_776_lot_procurement_innovation_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:ProcurementProject>
                <cac:ProcurementAdditionalType>
                    <cbc:ProcurementTypeCode listName="innovative-acquisition">proc-innov</cbc:ProcurementTypeCode>
                </cac:ProcurementAdditionalType>
            </cac:ProcurementProject>
        </cac:ProcurementProjectLot>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0002</cbc:ID>
            <cac:ProcurementProject>
                <cac:ProcurementAdditionalType>
                    <cbc:ProcurementTypeCode listName="innovative-acquisition">mar-nov</cbc:ProcurementTypeCode>
                </cac:ProcurementAdditionalType>
            </cac:ProcurementProject>
        </cac:ProcurementProjectLot>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0003</cbc:ID>
            <cac:ProcurementProject>
                <cac:ProcurementAdditionalType>
                    <cbc:ProcurementTypeCode listName="other-type">not-innovation</cbc:ProcurementTypeCode>
                </cac:ProcurementAdditionalType>
            </cac:ProcurementProject>
        </cac:ProcurementProjectLot>
    </root>
    """
    xml_file = tmp_path / "test_input_procurement_innovation.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open('output.json', 'r') as f:
        result = json.load(f)

    assert "tender" in result
    assert "lots" in result["tender"]
    
    innovation_lots = [lot for lot in result["tender"]["lots"] if "sustainability" in lot]
    assert len(innovation_lots) == 2

    lot_1 = next((lot for lot in innovation_lots if lot["id"] == "LOT-0001"), None)
    assert lot_1 is not None
    assert lot_1["hasSustainability"] is True
    assert len(lot_1["sustainability"]) == 1
    assert lot_1["sustainability"][0]["goal"] == "economic.processInnovation"

    lot_2 = next((lot for lot in innovation_lots if lot["id"] == "LOT-0002"), None)
    assert lot_2 is not None
    assert lot_2["hasSustainability"] is True
    assert len(lot_2["sustainability"]) == 1
    assert lot_2["sustainability"][0]["goal"] == "economic.marketInnovationPromotion"

    lot_3 = next((lot for lot in result["tender"]["lots"] if lot["id"] == "LOT-0003"), None)
    assert lot_3 is not None
    assert "sustainability" not in lot_3

if __name__ == "__main__":
    pytest.main()