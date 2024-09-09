# tests/test_BT_540_Lot.py

import pytest
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main
from converters.BT_540_Lot import (
    parse_award_criterion_description,
    merge_award_criterion_description,
)


def test_parse_award_criterion_description():
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:TenderingTerms>
                <cac:AwardingTerms>
                    <cac:AwardingCriterion>
                        <cac:SubordinateAwardingCriterion>
                            <cbc:Description>Tenders with a quality score less than 65...</cbc:Description>
                        </cac:SubordinateAwardingCriterion>
                    </cac:AwardingCriterion>
                </cac:AwardingTerms>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </root>
    """

    result = parse_award_criterion_description(xml_content)

    assert result is not None
    assert "tender" in result
    assert "lots" in result["tender"]
    assert len(result["tender"]["lots"]) == 1

    lot = result["tender"]["lots"][0]
    assert lot["id"] == "LOT-0001"
    assert "awardCriteria" in lot
    assert "criteria" in lot["awardCriteria"]
    assert len(lot["awardCriteria"]["criteria"]) == 1
    assert (
        lot["awardCriteria"]["criteria"][0]["description"]
        == "Tenders with a quality score less than 65..."
    )


def test_merge_award_criterion_description():
    release_json = {
        "tender": {
            "lots": [
                {"id": "LOT-0001", "awardCriteria": {"criteria": [{"type": "quality"}]}}
            ]
        }
    }

    award_criterion_description_data = {
        "tender": {
            "lots": [
                {
                    "id": "LOT-0001",
                    "awardCriteria": {
                        "criteria": [
                            {
                                "description": "Tenders with a quality score less than 65..."
                            }
                        ]
                    },
                },
                {
                    "id": "LOT-0002",
                    "awardCriteria": {
                        "criteria": [{"description": "Another criterion description"}]
                    },
                },
            ]
        }
    }

    merge_award_criterion_description(release_json, award_criterion_description_data)

    assert len(release_json["tender"]["lots"]) == 2

    lot1 = release_json["tender"]["lots"][0]
    assert lot1["id"] == "LOT-0001"
    assert len(lot1["awardCriteria"]["criteria"]) == 2
    assert {"type": "quality"} in lot1["awardCriteria"]["criteria"]
    assert {"description": "Tenders with a quality score less than 65..."} in lot1[
        "awardCriteria"
    ]["criteria"]

    lot2 = release_json["tender"]["lots"][1]
    assert lot2["id"] == "LOT-0002"
    assert len(lot2["awardCriteria"]["criteria"]) == 1
    assert (
        lot2["awardCriteria"]["criteria"][0]["description"]
        == "Another criterion description"
    )


def test_bt_540_lot_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:TenderingTerms>
                <cac:AwardingTerms>
                    <cac:AwardingCriterion>
                        <cac:SubordinateAwardingCriterion>
                            <cbc:Description>Tenders with a quality score less than 65...</cbc:Description>
                        </cac:SubordinateAwardingCriterion>
                    </cac:AwardingCriterion>
                </cac:AwardingTerms>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </root>
    """
    xml_file = tmp_path / "test_input_bt_540_lot.xml"
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
    assert (
        lot["awardCriteria"]["criteria"][0]["description"]
        == "Tenders with a quality score less than 65..."
    )


if __name__ == "__main__":
    pytest.main()
