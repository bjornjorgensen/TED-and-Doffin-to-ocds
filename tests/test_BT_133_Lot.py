# tests/test_BT_133_Lot.py

import pytest
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main

def test_bt_133_lot_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:TenderingProcess>
                <cac:OpenTenderEvent>
                    <cac:OccurenceLocation>
                        <cbc:Description languageID="ENG">online at URL https://event-on-line.org/d22f65 ...</cbc:Description>
                    </cac:OccurenceLocation>
                </cac:OpenTenderEvent>
            </cac:TenderingProcess>
        </cac:ProcurementProjectLot>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0002</cbc:ID>
            <cac:TenderingProcess>
                <cac:OpenTenderEvent>
                    <cac:OccurenceLocation>
                        <cbc:Description languageID="ENG">City Hall, Room 123, 1 Main Street, Anytown</cbc:Description>
                    </cac:OccurenceLocation>
                </cac:OpenTenderEvent>
            </cac:TenderingProcess>
        </cac:ProcurementProjectLot>
    </root>
    """
    xml_file = tmp_path / "test_input_public_opening_place.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open('output.json', 'r') as f:
        result = json.load(f)

    assert "tender" in result, "Expected 'tender' in result"
    assert "lots" in result["tender"], "Expected 'lots' in result['tender']"
    assert len(result["tender"]["lots"]) == 2, f"Expected 2 lots, got {len(result['tender']['lots'])}"

    lot_1 = next(lot for lot in result["tender"]["lots"] if lot["id"] == "LOT-0001")
    assert "bidOpening" in lot_1, "Expected 'bidOpening' in LOT-0001"
    assert "location" in lot_1["bidOpening"], "Expected 'location' in LOT-0001 bidOpening"
    assert lot_1["bidOpening"]["location"]["description"] == "online at URL https://event-on-line.org/d22f65 ...", "Unexpected description for LOT-0001"

    lot_2 = next(lot for lot in result["tender"]["lots"] if lot["id"] == "LOT-0002")
    assert "bidOpening" in lot_2, "Expected 'bidOpening' in LOT-0002"
    assert "location" in lot_2["bidOpening"], "Expected 'location' in LOT-0002 bidOpening"
    assert lot_2["bidOpening"]["location"]["description"] == "City Hall, Room 123, 1 Main Street, Anytown", "Unexpected description for LOT-0002"

if __name__ == "__main__":
    pytest.main()