# tests/test_BT_539_LotsGroup.py

import pytest
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main
from converters.BT_539_LotsGroup import parse_award_criterion_type_lots_group, merge_award_criterion_type_lots_group

def test_parse_award_criterion_type_lots_group():
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="LotsGroup">GLO-0001</cbc:ID>
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
    
    result = parse_award_criterion_type_lots_group(xml_content)
    
    assert result is not None
    assert "tender" in result
    assert "lotGroups" in result["tender"]
    assert len(result["tender"]["lotGroups"]) == 1
    
    lot_group = result["tender"]["lotGroups"][0]
    assert lot_group["id"] == "GLO-0001"
    assert "awardCriteria" in lot_group
    assert "criteria" in lot_group["awardCriteria"]
    assert len(lot_group["awardCriteria"]["criteria"]) == 1
    assert lot_group["awardCriteria"]["criteria"][0]["type"] == "quality"

def test_merge_award_criterion_type_lots_group():
    release_json = {
        "tender": {
            "lotGroups": [
                {
                    "id": "GLO-0001",
                    "awardCriteria": {
                        "criteria": [
                            {"type": "price"}
                        ]
                    }
                }
            ]
        }
    }
    
    award_criterion_type_data = {
        "tender": {
            "lotGroups": [
                {
                    "id": "GLO-0001",
                    "awardCriteria": {
                        "criteria": [
                            {"type": "quality"}
                        ]
                    }
                },
                {
                    "id": "GLO-0002",
                    "awardCriteria": {
                        "criteria": [
                            {"type": "cost"}
                        ]
                    }
                }
            ]
        }
    }
    
    merge_award_criterion_type_lots_group(release_json, award_criterion_type_data)
    
    assert len(release_json["tender"]["lotGroups"]) == 2
    
    lot_group1 = release_json["tender"]["lotGroups"][0]
    assert lot_group1["id"] == "GLO-0001"
    assert len(lot_group1["awardCriteria"]["criteria"]) == 2
    assert {"type": "price"} in lot_group1["awardCriteria"]["criteria"]
    assert {"type": "quality"} in lot_group1["awardCriteria"]["criteria"]
    
    lot_group2 = release_json["tender"]["lotGroups"][1]
    assert lot_group2["id"] == "GLO-0002"
    assert len(lot_group2["awardCriteria"]["criteria"]) == 1
    assert lot_group2["awardCriteria"]["criteria"][0]["type"] == "cost"

def test_bt_539_lots_group_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="LotsGroup">GLO-0001</cbc:ID>
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
    xml_file = tmp_path / "test_input_bt_539_lots_group.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open('output.json', 'r') as f:
        result = json.load(f)

    assert "tender" in result
    assert "lotGroups" in result["tender"]
    assert len(result["tender"]["lotGroups"]) == 1
    
    lot_group = result["tender"]["lotGroups"][0]
    assert lot_group["id"] == "GLO-0001"
    assert "awardCriteria" in lot_group
    assert "criteria" in lot_group["awardCriteria"]
    assert len(lot_group["awardCriteria"]["criteria"]) == 1
    assert lot_group["awardCriteria"]["criteria"][0]["type"] == "quality"

if __name__ == "__main__":
    pytest.main()