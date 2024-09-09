# tests/test_BT_539_Lot.py

import pytest
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main
from converters.BT_539_Lot import parse_award_criterion_type, merge_award_criterion_type


def test_parse_award_criterion_type():
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:TenderingTerms>
                <cac:AwardingTerms>
                    <cac:AwardingCriterion>
                        <cac:SubordinateAwardingCriterion>
                            <cbc:AwardingCriterionTypeCode listName="award-criterion-type">quality</cbc:AwardingCriterionTypeCode>
                        </cac:SubordinateAwardingCriterion>
                    </cac:AwardingCriterion>
                </cac:AwardingTerms>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </root>
    """

    result = parse_award_criterion_type(xml_content)

    assert result is not None
    assert "tender" in result
    assert "lots" in result["tender"]
    assert len(result["tender"]["lots"]) == 1

    lot = result["tender"]["lots"][0]
    assert lot["id"] == "LOT-0001"
    assert "awardCriteria" in lot
    assert "criteria" in lot["awardCriteria"]
    assert len(lot["awardCriteria"]["criteria"]) == 1
    assert lot["awardCriteria"]["criteria"][0]["type"] == "quality"


def test_merge_award_criterion_type():
    release_json = {
        "tender": {
            "lots": [
                {"id": "LOT-0001", "awardCriteria": {"criteria": [{"type": "price"}]}}
            ]
        }
    }

    award_criterion_type_data = {
        "tender": {
            "lots": [
                {
                    "id": "LOT-0001",
                    "awardCriteria": {"criteria": [{"type": "quality"}]},
                },
                {"id": "LOT-0002", "awardCriteria": {"criteria": [{"type": "cost"}]}},
            ]
        }
    }

    merge_award_criterion_type(release_json, award_criterion_type_data)

    assert len(release_json["tender"]["lots"]) == 2

    lot1 = release_json["tender"]["lots"][0]
    assert lot1["id"] == "LOT-0001"
    assert len(lot1["awardCriteria"]["criteria"]) == 2
    assert {"type": "price"} in lot1["awardCriteria"]["criteria"]
    assert {"type": "quality"} in lot1["awardCriteria"]["criteria"]

    lot2 = release_json["tender"]["lots"][1]
    assert lot2["id"] == "LOT-0002"
    assert len(lot2["awardCriteria"]["criteria"]) == 1
    assert lot2["awardCriteria"]["criteria"][0]["type"] == "cost"


def test_bt_539_lot_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:TenderingTerms>
                <cac:AwardingTerms>
                    <cac:AwardingCriterion>
                        <cac:SubordinateAwardingCriterion>
                            <cbc:AwardingCriterionTypeCode listName="award-criterion-type">quality</cbc:AwardingCriterionTypeCode>
                        </cac:SubordinateAwardingCriterion>
                    </cac:AwardingCriterion>
                </cac:AwardingTerms>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </root>
    """
    xml_file = tmp_path / "test_input_bt_539_lot.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open("output.json") as f:
        result = json.load(f)

    assert "tender" in result
    assert "lots" in result["tender"]
    assert len(result["tender"]["lots"]) == 1

    lot = result["tender"]["lots"][0]
    assert lot["id"] == "LOT-0001"
    assert "awardCriteria" in lot
    assert "criteria" in lot["awardCriteria"]
    assert len(lot["awardCriteria"]["criteria"]) == 1
    assert lot["awardCriteria"]["criteria"][0]["type"] == "quality"


if __name__ == "__main__":
    pytest.main()
