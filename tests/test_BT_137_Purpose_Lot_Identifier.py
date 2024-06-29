# tests/test_BT_137_Purpose_Lot_Identifier.py

import pytest
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main

def test_bt_137_purpose_lot_identifier_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
        </cac:ProcurementProjectLot>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0002</cbc:ID>
        </cac:ProcurementProjectLot>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="LotsGroup">GLO-0001</cbc:ID>
        </cac:ProcurementProjectLot>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Part">PAR-0000</cbc:ID>
        </cac:ProcurementProjectLot>
    </root>
    """
    xml_file = tmp_path / "test_input_purpose_lot_identifier.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open('output.json', 'r') as f:
        result = json.load(f)

    assert "tender" in result, "Expected 'tender' in result"
    assert "lots" in result["tender"], "Expected 'lots' in result['tender']"
    assert len(result["tender"]["lots"]) == 2, f"Expected 2 lots, got {len(result['tender']['lots'])}"
    assert {"id": "LOT-0001"} in result["tender"]["lots"], "Expected LOT-0001 in lots"
    assert {"id": "LOT-0002"} in result["tender"]["lots"], "Expected LOT-0002 in lots"

    assert "lotGroups" in result["tender"], "Expected 'lotGroups' in result['tender']"
    assert len(result["tender"]["lotGroups"]) == 1, f"Expected 1 lot group, got {len(result['tender']['lotGroups'])}"
    assert {"id": "GLO-0001"} in result["tender"]["lotGroups"], "Expected GLO-0001 in lotGroups"

    assert "id" in result["tender"], "Expected 'id' in result['tender']"
    assert result["tender"]["id"] == "PAR-0000", f"Expected tender id to be 'PAR-0000', got {result['tender']['id']}"

if __name__ == "__main__":
    pytest.main()