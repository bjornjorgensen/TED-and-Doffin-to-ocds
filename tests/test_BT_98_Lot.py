# tests/test_BT_98_Lot.py

import pytest
from lxml import etree
import json
import os
import sys

# Add the parent directory to sys.path to import main and BT_98_Lot
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main
from converters.BT_98_Lot import parse_tender_validity_deadline, merge_tender_validity_deadline

def create_xml_with_tender_validity(lot_id, duration, unit_code):
    xml_template = f"""
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">{lot_id}</cbc:ID>
            <cac:TenderingTerms>
                <cac:TenderValidityPeriod>
                    <cbc:DurationMeasure unitCode="{unit_code}">{duration}</cbc:DurationMeasure>
                </cac:TenderValidityPeriod>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </root>
    """
    return etree.fromstring(xml_template.encode())

def test_parse_tender_validity_deadline():
    xml_content = create_xml_with_tender_validity("LOT-0001", "4", "MONTH")
    result = parse_tender_validity_deadline(etree.tostring(xml_content))

    assert result == {
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

def test_merge_tender_validity_deadline():
    existing_json = {
        "tender": {
            "lots": [
                {
                    "id": "LOT-0001",
                    "title": "Existing Lot"
                }
            ]
        }
    }

    new_data = {
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

    merge_tender_validity_deadline(existing_json, new_data)

    assert existing_json == {
        "tender": {
            "lots": [
                {
                    "id": "LOT-0001",
                    "title": "Existing Lot",
                    "submissionTerms": {
                        "bidValidityPeriod": {
                            "durationInDays": 120
                        }
                    }
                }
            ]
        }
    }

def test_main_integration_tender_validity_deadline(tmp_path):
    xml_content = f"""
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
    xml_file = tmp_path / "test_input_tender_validity.xml"
    xml_file.write_text(xml_content)

    # Run the main function
    main(str(xml_file), "ocds-test-prefix")

    # Read the output JSON file
    with open('output.json', 'r') as f:
        result = json.load(f)

    # Check the result
    assert "tender" in result
    assert "lots" in result["tender"]
    assert len(result["tender"]["lots"]) == 1
    lot = result["tender"]["lots"][0]
    
    assert lot["id"] == "LOT-0001"
    assert "submissionTerms" in lot
    assert "bidValidityPeriod" in lot["submissionTerms"]
    assert lot["submissionTerms"]["bidValidityPeriod"]["durationInDays"] == 120

@pytest.mark.parametrize("duration,unit_code,expected_days", [
    (1, "DAY", 1),
    (2, "WEEK", 14),
    (3, "MONTH", 90),
    (1, "YEAR", 365),
])
def test_different_duration_units(duration, unit_code, expected_days):
    xml_content = create_xml_with_tender_validity("LOT-0001", str(duration), unit_code)
    result = parse_tender_validity_deadline(etree.tostring(xml_content))

    assert result["tender"]["lots"][0]["submissionTerms"]["bidValidityPeriod"]["durationInDays"] == expected_days

def test_no_tender_validity_deadline():
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:TenderingTerms>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </root>
    """
    result = parse_tender_validity_deadline(xml_content)
    assert result == {"tender": {"lots": []}}

if __name__ == "__main__":
    pytest.main()