# tests/test_BT_23.py

import pytest
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main

def test_bt_23_main_nature_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:ProcurementProject>
                <cbc:ProcurementTypeCode listName="contract-nature">works</cbc:ProcurementTypeCode>
            </cac:ProcurementProject>
        </cac:ProcurementProjectLot>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0002</cbc:ID>
            <cac:ProcurementProject>
                <cbc:ProcurementTypeCode listName="contract-nature">supplies</cbc:ProcurementTypeCode>
            </cac:ProcurementProject>
        </cac:ProcurementProjectLot>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Part">PART-0001</cbc:ID>
            <cac:ProcurementProject>
                <cbc:ProcurementTypeCode listName="contract-nature">services</cbc:ProcurementTypeCode>
            </cac:ProcurementProject>
        </cac:ProcurementProjectLot>
        <cac:ProcurementProject>
            <cbc:ProcurementTypeCode listName="contract-nature">works</cbc:ProcurementTypeCode>
        </cac:ProcurementProject>
    </root>
    """
    xml_file = tmp_path / "test_input_main_nature.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open('output.json', 'r') as f:
        result = json.load(f)

    assert "tender" in result
    assert "lots" in result["tender"]
    assert "mainProcurementCategory" in result["tender"]

    assert len(result["tender"]["lots"]) == 2
    assert result["tender"]["lots"][0]["id"] == "LOT-0001"
    assert result["tender"]["lots"][0]["mainProcurementCategory"] == "works"
    assert result["tender"]["lots"][1]["id"] == "LOT-0002"
    assert result["tender"]["lots"][1]["mainProcurementCategory"] == "goods"

    assert result["tender"]["mainProcurementCategory"] == "services"

if __name__ == "__main__":
    pytest.main()