# tests/test_BT_729_Lot.py

import pytest
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main

def test_bt_729_lot_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:TenderingTerms>
                <cac:AllowedSubcontractTerms>
                    <cbc:SubcontractingConditionsCode listName="subcontracting-obligation"/>
                    <cbc:MaximumPercent>45.5</cbc:MaximumPercent>
                </cac:AllowedSubcontractTerms>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </root>
    """
    xml_file = tmp_path / "test_input_lot_subcontracting_obligation_maximum.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open('output.json', 'r') as f:
        result = json.load(f)

    assert "tender" in result, "Expected 'tender' in result"
    assert "lots" in result["tender"], "Expected 'lots' in tender"
    assert len(result["tender"]["lots"]) == 1, f"Expected 1 lot, got {len(result['tender']['lots'])}"

    lot = result["tender"]["lots"][0]
    assert lot["id"] == "LOT-0001", f"Expected lot id 'LOT-0001', got {lot['id']}"
    assert "subcontractingTerms" in lot, "Expected 'subcontractingTerms' in lot"
    assert "competitiveMaximumPercentage" in lot["subcontractingTerms"], "Expected 'competitiveMaximumPercentage' in subcontractingTerms"
    assert lot["subcontractingTerms"]["competitiveMaximumPercentage"] == 0.455, \
        f"Expected competitiveMaximumPercentage 0.455, got {lot['subcontractingTerms']['competitiveMaximumPercentage']}"

if __name__ == "__main__":
    pytest.main()