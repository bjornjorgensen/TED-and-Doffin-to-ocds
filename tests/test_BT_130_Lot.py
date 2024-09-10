# tests/test_BT_130_Lot.py

import pytest
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.ted_and_doffin_to_ocds.main import main


def test_bt_130_lot_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:TenderingProcess>
                <cac:InvitationSubmissionPeriod>
                    <cbc:StartDate>2019-11-15+01:00</cbc:StartDate>
                </cac:InvitationSubmissionPeriod>
            </cac:TenderingProcess>
        </cac:ProcurementProjectLot>
    </root>
    """
    xml_file = tmp_path / "test_input_dispatch_invitation_tender.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open("output.json") as f:
        result = json.load(f)

    assert "tender" in result, "Expected 'tender' in result"
    assert "lots" in result["tender"], "Expected 'lots' in tender"
    assert (
        len(result["tender"]["lots"]) == 1
    ), f"Expected 1 lot, got {len(result['tender']['lots'])}"

    lot = result["tender"]["lots"][0]
    assert lot["id"] == "LOT-0001", f"Expected lot id 'LOT-0001', got {lot['id']}"
    assert "secondStage" in lot, "Expected 'secondStage' in lot"
    assert (
        "invitationDate" in lot["secondStage"]
    ), "Expected 'invitationDate' in secondStage"
    assert (
        lot["secondStage"]["invitationDate"] == "2019-11-15T00:00:00+01:00"
    ), f"Expected invitationDate '2019-11-15T00:00:00+01:00', got {lot['secondStage']['invitationDate']}"


if __name__ == "__main__":
    pytest.main()
