# tests/test_BT_99_Lot.py

import pytest
from lxml import etree
import json
import os
import sys

# Add the parent directory to sys.path to import main and BT_99_Lot
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main
from converters.BT_99_Lot import parse_review_deadline_description, merge_review_deadline_description

def create_xml_with_review_deadline(lot_id, description):
    xml_template = f"""
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">{lot_id}</cbc:ID>
            <cac:TenderingTerms>
                <cac:AppealTerms>
                    <cac:PresentationPeriod>
                        <cbc:Description>{description}</cbc:Description>
                    </cac:PresentationPeriod>
                </cac:AppealTerms>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </root>
    """
    return etree.fromstring(xml_template.encode())

def test_parse_review_deadline_description():
    description = "Any review request shall be submitted ..."
    xml_content = create_xml_with_review_deadline("LOT-0001", description)
    result = parse_review_deadline_description(etree.tostring(xml_content))

    assert result == {
        "tender": {
            "lots": [
                {
                    "id": "LOT-0001",
                    "reviewDetails": description
                }
            ]
        }
    }

def test_merge_review_deadline_description():
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
                    "reviewDetails": "Any review request shall be submitted ..."
                }
            ]
        }
    }

    merge_review_deadline_description(existing_json, new_data)

    assert existing_json == {
        "tender": {
            "lots": [
                {
                    "id": "LOT-0001",
                    "title": "Existing Lot",
                    "reviewDetails": "Any review request shall be submitted ..."
                }
            ]
        }
    }

def test_main_integration_review_deadline_description(tmp_path):
    description = "Any review request shall be submitted ..."
    xml_content = f"""
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:TenderingTerms>
                <cac:AppealTerms>
                    <cac:PresentationPeriod>
                        <cbc:Description>{description}</cbc:Description>
                    </cac:PresentationPeriod>
                </cac:AppealTerms>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </root>
    """
    xml_file = tmp_path / "test_input_review_deadline.xml"
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
    assert "reviewDetails" in lot
    assert lot["reviewDetails"] == description

def test_no_review_deadline_description():
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
    result = parse_review_deadline_description(xml_content)
    assert result == {"tender": {"lots": []}}

if __name__ == "__main__":
    pytest.main()