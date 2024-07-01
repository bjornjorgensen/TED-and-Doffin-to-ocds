# tests/test_BT_24.py

import pytest
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main

def test_bt_24_description_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:ProcurementProject>
                <cbc:Description languageID="ENG">Description for Lot 1</cbc:Description>
            </cac:ProcurementProject>
        </cac:ProcurementProjectLot>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="LotsGroup">GLO-0001</cbc:ID>
            <cac:ProcurementProject>
                <cbc:Description languageID="ENG">Description for Lots Group 1</cbc:Description>
            </cac:ProcurementProject>
        </cac:ProcurementProjectLot>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Part">PART-0001</cbc:ID>
            <cac:ProcurementProject>
                <cbc:Description languageID="ENG">Description for Part</cbc:Description>
            </cac:ProcurementProject>
        </cac:ProcurementProjectLot>
        <cac:ProcurementProject>
            <cbc:Description languageID="ENG">Description for Procedure</cbc:Description>
        </cac:ProcurementProject>
    </root>
    """
    xml_file = tmp_path / "test_input_description.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open('output.json', 'r') as f:
        result = json.load(f)

    assert "tender" in result
    assert "lots" in result["tender"]
    assert "lotGroups" in result["tender"]
    assert "description" in result["tender"]

    assert len(result["tender"]["lots"]) == 1
    assert result["tender"]["lots"][0]["id"] == "LOT-0001"
    assert result["tender"]["lots"][0]["description"] == "Description for Lot 1"

    assert len(result["tender"]["lotGroups"]) == 1
    assert result["tender"]["lotGroups"][0]["id"] == "GLO-0001"
    assert result["tender"]["lotGroups"][0]["description"] == "Description for Lots Group 1"

    assert result["tender"]["description"] == "Description for Part"

if __name__ == "__main__":
    pytest.main()