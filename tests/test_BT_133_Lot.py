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
                        <cbc:Description>online at URL https://event-on-line.org/d22f65 ...</cbc:Description>
                    </cac:OccurenceLocation>
                </cac:OpenTenderEvent>
            </cac:TenderingProcess>
        </cac:ProcurementProjectLot>
    </root>
    """
    xml_file = tmp_path / "test_input_lot_bid_opening.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open("output.json", "r") as f:
        result = json.load(f)

    assert "tender" in result, "Expected 'tender' in result"
    assert "lots" in result["tender"], "Expected 'lots' in tender"
    assert (
        len(result["tender"]["lots"]) == 1
    ), f"Expected 1 lot, got {len(result['tender']['lots'])}"

    lot = result["tender"]["lots"][0]
    assert lot["id"] == "LOT-0001", f"Expected lot id 'LOT-0001', got {lot['id']}"
    assert "bidOpening" in lot, "Expected 'bidOpening' in lot"
    assert "location" in lot["bidOpening"], "Expected 'location' in bidOpening"
    assert (
        "description" in lot["bidOpening"]["location"]
    ), "Expected 'description' in location"
    expected_description = "online at URL https://event-on-line.org/d22f65 ..."
    assert (
        lot["bidOpening"]["location"]["description"] == expected_description
    ), f"Expected description '{expected_description}', got {lot['bidOpening']['location']['description']}"


if __name__ == "__main__":
    pytest.main()
