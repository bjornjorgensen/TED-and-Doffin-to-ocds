# tests/test_BT_771_Lot.py

import pytest
from lxml import etree
from converters.BT_771_Lot import parse_late_tenderer_info, merge_late_tenderer_info
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main
def test_parse_late_tenderer_info():
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:TenderingTerms>
                <cac:TendererQualificationRequest>
                    <cac:SpecificTendererRequirement>
                        <cbc:TendererRequirementTypeCode listName="missing-info-submission">late-all</cbc:TendererRequirementTypeCode>
                    </cac:SpecificTendererRequirement>
                </cac:TendererQualificationRequest>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </root>
    """
    
    result = parse_late_tenderer_info(xml_content)
    
    assert result is not None
    assert "tender" in result
    assert "lots" in result["tender"]
    assert len(result["tender"]["lots"]) == 1
    assert result["tender"]["lots"][0]["id"] == "LOT-0001"
    assert "submissionMethodDetails" in result["tender"]["lots"][0]
    assert "all missing tenderer-related documents may be submitted later" in result["tender"]["lots"][0]["submissionMethodDetails"]

def test_merge_late_tenderer_info():
    release_json = {
        "tender": {
            "lots": [
                {
                    "id": "LOT-0001",
                    "title": "Existing Lot"
                }
            ]
        }
    }
    
    late_tenderer_info = {
        "tender": {
            "lots": [
                {
                    "id": "LOT-0001",
                    "submissionMethodDetails": "At the discretion of the buyer, all missing tenderer-related documents may be submitted later."
                }
            ]
        }
    }
    
    merge_late_tenderer_info(release_json, late_tenderer_info)
    
    assert "submissionMethodDetails" in release_json["tender"]["lots"][0]
    assert "all missing tenderer-related documents may be submitted later" in release_json["tender"]["lots"][0]["submissionMethodDetails"]

def test_bt_771_lot_late_tenderer_info_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:TenderingTerms>
                <cac:TendererQualificationRequest>
                    <cac:SpecificTendererRequirement>
                        <cbc:TendererRequirementTypeCode listName="missing-info-submission">late-all</cbc:TendererRequirementTypeCode>
                    </cac:SpecificTendererRequirement>
                </cac:TendererQualificationRequest>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0002</cbc:ID>
            <cac:TenderingTerms>
                <cac:TendererQualificationRequest>
                    <cac:SpecificTendererRequirement>
                        <cbc:TendererRequirementTypeCode listName="missing-info-submission">late-none</cbc:TendererRequirementTypeCode>
                    </cac:SpecificTendererRequirement>
                </cac:TendererQualificationRequest>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0003</cbc:ID>
            <cac:TenderingTerms>
                <cac:TendererQualificationRequest>
                    <cac:SpecificTendererRequirement>
                        <cbc:TendererRequirementTypeCode listName="other-requirement">not-late-info</cbc:TendererRequirementTypeCode>
                    </cac:SpecificTendererRequirement>
                </cac:TendererQualificationRequest>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </root>
    """
    xml_file = tmp_path / "test_input_late_tenderer_info.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open('output.json', 'r') as f:
        result = json.load(f)

    assert "tender" in result
    assert "lots" in result["tender"]
    
    lots_with_info = [lot for lot in result["tender"]["lots"] if "submissionMethodDetails" in lot]
    assert len(lots_with_info) == 2

    lot_1 = next((lot for lot in lots_with_info if lot["id"] == "LOT-0001"), None)
    assert lot_1 is not None
    assert "all missing tenderer-related documents may be submitted later" in lot_1["submissionMethodDetails"]

    lot_2 = next((lot for lot in lots_with_info if lot["id"] == "LOT-0002"), None)
    assert lot_2 is not None
    assert "No documents can be submitted later" in lot_2["submissionMethodDetails"]

    lot_3 = next((lot for lot in result["tender"]["lots"] if lot["id"] == "LOT-0003"), None)
    assert lot_3 is not None
    assert "submissionMethodDetails" not in lot_3

if __name__ == "__main__":
    pytest.main()