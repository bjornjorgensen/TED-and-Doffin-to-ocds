# tests/test_BT_135_Procedure.py

import pytest
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main

def test_bt_135_procedure_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:TenderingProcess>
            <cac:ProcessJustification>
                <cbc:ProcessReasonCode listName="direct-award-justification">code</cbc:ProcessReasonCode>
                <cbc:ProcessReason>Direct award is justified ...</cbc:ProcessReason>
            </cac:ProcessJustification>
        </cac:TenderingProcess>
    </root>
    """
    xml_file = tmp_path / "test_input_direct_award_justification.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open('output.json', 'r') as f:
        result = json.load(f)

    assert "tender" in result, "Expected 'tender' in result"
    assert "procurementMethodRationale" in result["tender"], "Expected 'procurementMethodRationale' in tender"
    assert result["tender"]["procurementMethodRationale"] == "Direct award is justified ...", "Unexpected procurementMethodRationale value"

if __name__ == "__main__":
    pytest.main()