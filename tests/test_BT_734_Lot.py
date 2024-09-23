# tests/test_bt_734_Lot.py

import pytest
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.ted_and_doffin_to_ocds.main import main


def test_bt_734_lot_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:TenderingTerms>
                <cac:AwardingTerms>
                    <cac:AwardingCriterion>
                        <cac:SubordinateAwardingCriterion>
                            <cbc:Name languageID="ENG">Technical merit</cbc:Name>
                        </cac:SubordinateAwardingCriterion>
                        <cac:SubordinateAwardingCriterion>
                            <cbc:Name languageID="ENG">Price</cbc:Name>
                        </cac:SubordinateAwardingCriterion>
                    </cac:AwardingCriterion>
                </cac:AwardingTerms>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </root>
    """
    xml_file = tmp_path / "test_input_award_criterion_name.xml"
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
    assert "awardCriteria" in lot, "Expected 'awardCriteria' in lot"
    assert "criteria" in lot["awardCriteria"], "Expected 'criteria' in awardCriteria"
    assert (
        len(lot["awardCriteria"]["criteria"]) == 2
    ), f"Expected 2 criteria, got {len(lot['awardCriteria']['criteria'])}"

    criteria_names = [c["name"] for c in lot["awardCriteria"]["criteria"]]
    assert (
        "Technical merit" in criteria_names
    ), "Expected 'Technical merit' in criteria names"
    assert "Price" in criteria_names, "Expected 'Price' in criteria names"


if __name__ == "__main__":
    pytest.main()
