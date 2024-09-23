# tests/test_bt_44_Lot.py

import pytest
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.ted_and_doffin_to_ocds.main import main


def test_bt_44_lot_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
    xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
    <cac:ProcurementProjectLot>
    <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
    <cac:TenderingTerms>
    <cac:AwardingTerms>
    <cac:Prize>
    <cbc:RankCode>1</cbc:RankCode>
    </cac:Prize>
    <cac:Prize>
    <cbc:RankCode>2</cbc:RankCode>
    </cac:Prize>
    </cac:AwardingTerms>
    </cac:TenderingTerms>
    </cac:ProcurementProjectLot>
    </root>
    """
    xml_file = tmp_path / "test_input_prize_rank.xml"
    xml_file.write_text(xml_content)
    main(str(xml_file), "ocds-test-prefix")

    with open("output.json") as f:
        result = json.load(f)

    # Check the structure of the result
    assert "tender" in result, "Expected 'tender' in result"
    assert "lots" in result["tender"], "Expected 'lots' in tender"

    # Check the number of lots
    assert (
        len(result["tender"]["lots"]) == 1
    ), f"Expected 1 lot, got {len(result['tender']['lots'])}"

    lot = result["tender"]["lots"][0]

    # Check lot ID
    assert lot["id"] == "LOT-0001", f"Expected lot id 'LOT-0001', got {lot['id']}"

    # Check designContest structure
    assert "designContest" in lot, "Expected 'designContest' in lot"
    assert "prizes" in lot["designContest"], "Expected 'prizes' in designContest"
    assert "details" in lot["designContest"]["prizes"], "Expected 'details' in prizes"

    prizes = lot["designContest"]["prizes"]["details"]

    # Check number of prizes
    assert len(prizes) == 2, f"Expected 2 prizes, got {len(prizes)}"

    # Check first prize
    assert prizes[0]["id"] == "0", f"Expected first prize id '0', got {prizes[0]['id']}"
    assert (
        prizes[0]["rank"] == 1
    ), f"Expected first prize rank 1, got {prizes[0]['rank']}"

    # Check second prize
    assert (
        prizes[1]["id"] == "1"
    ), f"Expected second prize id '1', got {prizes[1]['id']}"
    assert (
        prizes[1]["rank"] == 2
    ), f"Expected second prize rank 2, got {prizes[1]['rank']}"


if __name__ == "__main__":
    pytest.main()
