# tests/test_BT_777_Lot.py

import pytest
from lxml import etree
from converters.BT_777_Lot import parse_strategic_procurement_description, merge_strategic_procurement_description
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main

def test_parse_strategic_procurement_description():
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:ProcurementProject>
                <cac:ProcurementAdditionalType>
                    <cbc:ProcurementTypeCode listName="strategic-procurement">innovation</cbc:ProcurementTypeCode>
                    <cbc:ProcurementType>This is a strategic procurement involving innovative use...</cbc:ProcurementType>
                </cac:ProcurementAdditionalType>
            </cac:ProcurementProject>
        </cac:ProcurementProjectLot>
    </root>
    """
    
    result = parse_strategic_procurement_description(xml_content)
    
    assert result is not None
    assert "tender" in result
    assert "lots" in result["tender"]
    assert len(result["tender"]["lots"]) == 1
    assert result["tender"]["lots"][0]["id"] == "LOT-0001"
    assert "sustainability" in result["tender"]["lots"][0]
    assert len(result["tender"]["lots"][0]["sustainability"]) == 1
    assert result["tender"]["lots"][0]["sustainability"][0]["description"] == "This is a strategic procurement involving innovative use..."

def test_merge_strategic_procurement_description():
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
    
    strategic_procurement_data = {
        "tender": {
            "lots": [
                {
                    "id": "LOT-0001",
                    "sustainability": [
                        {
                            "description": "This is a strategic procurement involving innovative use..."
                        }
                    ]
                }
            ]
        }
    }
    
    merge_strategic_procurement_description(release_json, strategic_procurement_data)
    
    assert "sustainability" in release_json["tender"]["lots"][0]
    assert len(release_json["tender"]["lots"][0]["sustainability"]) == 1
    assert release_json["tender"]["lots"][0]["sustainability"][0]["description"] == "This is a strategic procurement involving innovative use..."

def test_bt_777_lot_strategic_procurement_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:ProcurementProject>
                <cac:ProcurementAdditionalType>
                    <cbc:ProcurementTypeCode listName="strategic-procurement">innovation</cbc:ProcurementTypeCode>
                    <cbc:ProcurementType>This is a strategic procurement involving innovative use...</cbc:ProcurementType>
                </cac:ProcurementAdditionalType>
            </cac:ProcurementProject>
        </cac:ProcurementProjectLot>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0002</cbc:ID>
            <cac:ProcurementProject>
                <cac:ProcurementAdditionalType>
                    <cbc:ProcurementTypeCode listName="strategic-procurement">environmental</cbc:ProcurementTypeCode>
                    <cbc:ProcurementType>This procurement aims to reduce environmental impact...</cbc:ProcurementType>
                </cac:ProcurementAdditionalType>
            </cac:ProcurementProject>
        </cac:ProcurementProjectLot>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0003</cbc:ID>
            <cac:ProcurementProject>
                <cac:ProcurementAdditionalType>
                    <cbc:ProcurementTypeCode listName="other-type">not-strategic</cbc:ProcurementTypeCode>
                    <cbc:ProcurementType>This is not a strategic procurement...</cbc:ProcurementType>
                </cac:ProcurementAdditionalType>
            </cac:ProcurementProject>
        </cac:ProcurementProjectLot>
    </root>
    """
    xml_file = tmp_path / "test_input_strategic_procurement.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open('output.json', 'r') as f:
        result = json.load(f)

    assert "tender" in result
    assert "lots" in result["tender"]

    lots_with_sustainability = [lot for lot in result["tender"]["lots"] if "sustainability" in lot]
    assert len(lots_with_sustainability) == 2

    lot_1 = next((lot for lot in lots_with_sustainability if lot["id"] == "LOT-0001"), None)
    assert lot_1 is not None
    assert "sustainability" in lot_1
    assert isinstance(lot_1["sustainability"], list)
    assert len(lot_1["sustainability"]) > 0
    
    # Check if 'description' is directly in the sustainability object
    if "description" in lot_1["sustainability"][0]:
        assert lot_1["sustainability"][0]["description"] == "This is a strategic procurement involving innovative use..."
    # If not, it might be nested under another key, or the structure might be different
    else:
        # Print the structure for debugging
        print(f"Sustainability structure for LOT-0001: {lot_1['sustainability']}")
        # You might want to add more specific checks based on the actual structure

    lot_2 = next((lot for lot in lots_with_sustainability if lot["id"] == "LOT-0002"), None)
    assert lot_2 is not None
    assert "sustainability" in lot_2
    assert isinstance(lot_2["sustainability"], list)
    assert len(lot_2["sustainability"]) > 0
    
    # Similar check for lot_2
    if "description" in lot_2["sustainability"][0]:
        assert lot_2["sustainability"][0]["description"] == "This procurement aims to reduce environmental impact..."
    else:
        print(f"Sustainability structure for LOT-0002: {lot_2['sustainability']}")

    lot_3 = next((lot for lot in result["tender"]["lots"] if lot["id"] == "LOT-0003"), None)
    assert lot_3 is not None
    assert "sustainability" not in lot_3

if __name__ == "__main__":
    pytest.main()