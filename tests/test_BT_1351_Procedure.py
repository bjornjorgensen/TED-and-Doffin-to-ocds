# tests/test_BT_1351_Procedure.py

import pytest
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main

def test_bt_1351_accelerated_procedure_justification_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:TenderingProcess>
            <cac:ProcessJustification>
                <cbc:ProcessReasonCode listName="accelerated-procedure">code</cbc:ProcessReasonCode>
                <cbc:ProcessReason>Direct award is justified ...</cbc:ProcessReason>
            </cac:ProcessJustification>
        </cac:TenderingProcess>
    </root>
    """
    xml_file = tmp_path / "test_input_accelerated_procedure_justification.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open('output.json', 'r') as f:
        result = json.load(f)

    assert "tender" in result, "Expected 'tender' in result"
    assert "procedure" in result["tender"], "Expected 'procedure' in tender"
    assert "acceleratedRationale" in result["tender"]["procedure"], "Expected 'acceleratedRationale' in procedure"
    assert result["tender"]["procedure"]["acceleratedRationale"] == "Direct award is justified ...", f"Expected 'Direct award is justified ...', got {result['tender']['procedure']['acceleratedRationale']}"

if __name__ == "__main__":
    pytest.main()