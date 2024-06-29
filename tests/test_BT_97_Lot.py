# tests/test_BT_97_Lot.py

import pytest
import json
import os
from lxml import etree
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main

def create_xml_with_languages(lot_id, languages):
    xml_template = f"""
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">{lot_id}</cbc:ID>
            <cac:TenderingTerms>
                {''.join(f'<cac:Language><cbc:ID>{lang}</cbc:ID></cac:Language>' for lang in languages)}
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </root>
    """
    return xml_template

def test_main_with_submission_language(tmp_path):
    # Create a temporary XML file
    xml_content = create_xml_with_languages("LOT-0001", ["ENG", "FRA"])
    xml_file = tmp_path / "test_input.xml"
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
    assert result["tender"]["lots"][0]["id"] == "LOT-0001"
    assert "submissionTerms" in result["tender"]["lots"][0]
    assert "languages" in result["tender"]["lots"][0]["submissionTerms"]
    assert set(result["tender"]["lots"][0]["submissionTerms"]["languages"]) == {"en", "fr"}

def test_main_with_no_languages(tmp_path):
    # Create a temporary XML file with no languages
    xml_content = create_xml_with_languages("LOT-0001", [])
    xml_file = tmp_path / "test_input_no_languages.xml"
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
    assert result["tender"]["lots"][0]["id"] == "LOT-0001"
    assert "submissionTerms" not in result["tender"]["lots"][0] or "languages" not in result["tender"]["lots"][0]["submissionTerms"]

def test_main_with_multiple_lots(tmp_path):
    # Create a temporary XML file with multiple lots
    xml_content = f"""
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:TenderingTerms>
                <cac:Language><cbc:ID>ENG</cbc:ID></cac:Language>
                <cac:Language><cbc:ID>FRA</cbc:ID></cac:Language>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0002</cbc:ID>
            <cac:TenderingTerms>
                <cac:Language><cbc:ID>DEU</cbc:ID></cac:Language>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </root>
    """
    xml_file = tmp_path / "test_input_multiple_lots.xml"
    xml_file.write_text(xml_content)

    # Run the main function
    main(str(xml_file), "ocds-test-prefix")

    # Read the output JSON file
    with open('output.json', 'r') as f:
        result = json.load(f)

    # Check the result
    assert "tender" in result
    assert "lots" in result["tender"]
    assert len(result["tender"]["lots"]) == 2
    assert result["tender"]["lots"][0]["id"] == "LOT-0001"
    assert set(result["tender"]["lots"][0]["submissionTerms"]["languages"]) == {"en", "fr"}
    assert result["tender"]["lots"][1]["id"] == "LOT-0002"
    assert set(result["tender"]["lots"][1]["submissionTerms"]["languages"]) == {"de"}

if __name__ == "__main__":
    pytest.main()