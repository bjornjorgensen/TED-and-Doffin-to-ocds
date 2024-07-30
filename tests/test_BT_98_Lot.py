# tests/test_BT_98_Lot.py

import pytest
from lxml import etree
from converters.BT_98_Lot import parse_tender_validity_deadline, merge_tender_validity_deadline
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main

def test_parse_tender_validity_deadline():
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:TenderingTerms>
                <cac:TenderValidityPeriod>
                    <cbc:DurationMeasure unitCode="MONTH">4</cbc:DurationMeasure>
                </cac:TenderValidityPeriod>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </root>
    """
    
    result = parse_tender_validity_deadline(xml_content)
    
    assert result is not None
    assert "tender" in result
    assert "lots" in result["tender"]
    assert len(result["tender"]["lots"]) == 1
    assert result["tender"]["lots"][0]["id"] == "LOT-0001"
    assert result["tender"]["lots"][0]["submissionTerms"]["bidValidityPeriod"]["durationInDays"] == 120

def test_merge_tender_validity_deadline():
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
    
    tender_validity_deadline_data = {
        "tender": {
            "lots": [
                {
                    "id": "LOT-0001",
                    "submissionTerms": {
                        "bidValidityPeriod": {
                            "durationInDays": 120
                        }
                    }
                }
            ]
        }
    }
    
    merge_tender_validity_deadline(release_json, tender_validity_deadline_data)
    
    assert "submissionTerms" in release_json["tender"]["lots"][0]
    assert "bidValidityPeriod" in release_json["tender"]["lots"][0]["submissionTerms"]
    assert release_json["tender"]["lots"][0]["submissionTerms"]["bidValidityPeriod"]["durationInDays"] == 120

def test_bt_98_lot_tender_validity_deadline_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:TenderingTerms>
                <cac:TenderValidityPeriod>
                    <cbc:DurationMeasure unitCode="MONTH">4</cbc:DurationMeasure>
                </cac:TenderValidityPeriod>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0002</cbc:ID>
            <cac:TenderingTerms>
                <cac:TenderValidityPeriod>
                    <cbc:DurationMeasure unitCode="WEEK">6</cbc:DurationMeasure>
                </cac:TenderValidityPeriod>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </root>
    """
    xml_file = tmp_path / "test_input_tender_validity_deadline.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open('output.json', 'r') as f:
        result = json.load(f)

    assert "tender" in result
    assert "lots" in result["tender"]
    assert len(result["tender"]["lots"]) == 2

    lot_1 = next((lot for lot in result["tender"]["lots"] if lot["id"] == "LOT-0001"), None)
    assert lot_1 is not None
    assert lot_1["submissionTerms"]["bidValidityPeriod"]["durationInDays"] == 120

    lot_2 = next((lot for lot in result["tender"]["lots"] if lot["id"] == "LOT-0002"), None)
    assert lot_2 is not None
    assert lot_2["submissionTerms"]["bidValidityPeriod"]["durationInDays"] == 42

if __name__ == "__main__":
    pytest.main()