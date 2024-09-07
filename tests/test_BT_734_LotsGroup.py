# tests/test_BT_734_LotsGroup.py

import pytest
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main


def test_bt_734_lotsgroup_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="LotsGroup">GLO-0001</cbc:ID>
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
    xml_file = tmp_path / "test_input_award_criterion_name_lotsgroup.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open("output.json", "r") as f:
        result = json.load(f)

    assert "tender" in result, "Expected 'tender' in result"
    assert "lotGroups" in result["tender"], "Expected 'lotGroups' in tender"
    assert (
        len(result["tender"]["lotGroups"]) == 1
    ), f"Expected 1 lot group, got {len(result['tender']['lotGroups'])}"

    lot_group = result["tender"]["lotGroups"][0]
    assert (
        lot_group["id"] == "GLO-0001"
    ), f"Expected lot group id 'GLO-0001', got {lot_group['id']}"
    assert "awardCriteria" in lot_group, "Expected 'awardCriteria' in lot group"
    assert (
        "criteria" in lot_group["awardCriteria"]
    ), "Expected 'criteria' in awardCriteria"
    assert (
        len(lot_group["awardCriteria"]["criteria"]) == 2
    ), f"Expected 2 criteria, got {len(lot_group['awardCriteria']['criteria'])}"

    criteria_names = [c["name"] for c in lot_group["awardCriteria"]["criteria"]]
    assert (
        "Technical merit" in criteria_names
    ), "Expected 'Technical merit' in criteria names"
    assert "Price" in criteria_names, "Expected 'Price' in criteria names"


if __name__ == "__main__":
    pytest.main()
