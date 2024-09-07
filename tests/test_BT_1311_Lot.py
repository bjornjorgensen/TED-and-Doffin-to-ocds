# tests/test_BT_1311_Lot.py

import pytest
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main


def test_bt_1311_lot_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:TenderingProcess>
                <cac:ParticipationRequestReceptionPeriod>
                    <cbc:EndDate>2019-11-25+01:00</cbc:EndDate>
                    <cbc:EndTime>12:00:00+01:00</cbc:EndTime>
                </cac:ParticipationRequestReceptionPeriod>
            </cac:TenderingProcess>
        </cac:ProcurementProjectLot>
    </root>
    """
    xml_file = tmp_path / "test_input_deadline_receipt_requests.xml"
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
    assert "tenderPeriod" in lot, "Expected 'tenderPeriod' in lot"
    assert "endDate" in lot["tenderPeriod"], "Expected 'endDate' in tenderPeriod"
    assert (
        lot["tenderPeriod"]["endDate"] == "2019-11-25T12:00:00+01:00"
    ), f"Expected endDate '2019-11-25T12:00:00+01:00', got {lot['tenderPeriod']['endDate']}"


if __name__ == "__main__":
    pytest.main()
