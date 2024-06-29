# test_BT_22_23_24_integration.py

import pytest
import json
import os
from lxml import etree
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main

def create_test_xml(lot_id, internal_id, nature, description):
    xml_template = f"""
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">{lot_id}</cbc:ID>
            <cac:ProcurementProject>
                <cbc:ID schemeName="InternalID">{internal_id}</cbc:ID>
                <cbc:ProcurementTypeCode listName="contract-nature">{nature}</cbc:ProcurementTypeCode>
                <cbc:Description>{description}</cbc:Description>
            </cac:ProcurementProject>
        </cac:ProcurementProjectLot>
    </root>
    """
    return xml_template

def test_main_integration(tmp_path):
    # Create a temporary XML file
    xml_content = create_test_xml("LOT-0001", "PROC/2020/0024-ABC-FGHI", "works", "Test description")
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
    lot = result["tender"]["lots"][0]
    
    # Check BT-22
    assert lot["id"] == "LOT-0001"
    assert "identifiers" in lot
    assert len(lot["identifiers"]) == 1
    assert lot["identifiers"][0]["id"] == "PROC/2020/0024-ABC-FGHI"
    assert lot["identifiers"][0]["scheme"] == "internal"
    
    # Check BT-23
    assert lot["mainProcurementCategory"] == "works"
    
    # Check BT-24
    assert lot["description"] == "Test description"

def test_main_integration_supplies(tmp_path):
    # Create a temporary XML file with 'supplies' as nature
    xml_content = create_test_xml("LOT-0002", "PROC/2020/0025-XYZ", "supplies", "Another test description")
    xml_file = tmp_path / "test_input_supplies.xml"
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
    
    # Check BT-23 specifically for 'supplies' -> 'goods' conversion
    assert lot["mainProcurementCategory"] == "goods"

def test_main_integration_no_data(tmp_path):
    # Create a temporary XML file with no relevant data
    xml_content = "<root></root>"
    xml_file = tmp_path / "test_input_no_data.xml"
    xml_file.write_text(xml_content)

    # Run the main function
    main(str(xml_file), "ocds-test-prefix")

    # Read the output JSON file
    with open('output.json', 'r') as f:
        result = json.load(f)

    # Check the result
    assert "tender" in result
    assert "lots" not in result["tender"]

if __name__ == "__main__":
    pytest.main()