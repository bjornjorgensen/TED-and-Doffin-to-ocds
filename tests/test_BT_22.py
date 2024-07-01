# tests/test_BT_22.py

import pytest
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main

def test_bt_22_internal_identifiers_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:ProcurementProject>
                <cbc:ID schemeName="InternalID">PROC/2020/0024-ABC-FGHI</cbc:ID>
            </cac:ProcurementProject>
        </cac:ProcurementProjectLot>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="LotsGroup">GLO-0001</cbc:ID>
            <cac:ProcurementProject>
                <cbc:ID schemeName="InternalID">PROC/2020/0024-XYZ-KLMN</cbc:ID>
            </cac:ProcurementProject>
        </cac:ProcurementProjectLot>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Part">PART-0001</cbc:ID>
            <cac:ProcurementProject>
                <cbc:ID schemeName="InternalID">PROC/2020/0024-PART</cbc:ID>
            </cac:ProcurementProject>
        </cac:ProcurementProjectLot>
        <cac:ProcurementProject>
            <cbc:ID schemeName="InternalID">PROC/2020/0024-MAIN</cbc:ID>
        </cac:ProcurementProject>
    </root>
    """
    xml_file = tmp_path / "test_input_internal_identifiers.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open('output.json', 'r') as f:
        result = json.load(f)

    assert "tender" in result
    assert "lots" in result["tender"]
    assert "lotGroups" in result["tender"]
    assert "identifiers" in result["tender"]

    assert len(result["tender"]["lots"]) == 1
    assert result["tender"]["lots"][0]["id"] == "LOT-0001"
    assert result["tender"]["lots"][0]["identifiers"][0]["id"] == "PROC/2020/0024-ABC-FGHI"
    assert result["tender"]["lots"][0]["identifiers"][0]["scheme"] == "internal"

    assert len(result["tender"]["lotGroups"]) == 1
    assert result["tender"]["lotGroups"][0]["id"] == "GLO-0001"
    assert result["tender"]["lotGroups"][0]["identifiers"][0]["id"] == "PROC/2020/0024-XYZ-KLMN"
    assert result["tender"]["lotGroups"][0]["identifiers"][0]["scheme"] == "internal"

    assert len(result["tender"]["identifiers"]) == 2
    assert {"id": "PROC/2020/0024-PART", "scheme": "internal"} in result["tender"]["identifiers"]
    assert {"id": "PROC/2020/0024-MAIN", "scheme": "internal"} in result["tender"]["identifiers"]

if __name__ == "__main__":
    pytest.main()