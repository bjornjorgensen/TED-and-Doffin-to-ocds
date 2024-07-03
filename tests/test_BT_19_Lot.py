# tests/test_BT_19_Lot.py

import pytest
import json
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main

def test_bt_19_lot_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:TenderingProcess>
                <cac:ProcessJustification>
                    <cbc:ProcessReasonCode listName="no-esubmission-justification">phy-mod</cbc:ProcessReasonCode>
                </cac:ProcessJustification>
            </cac:TenderingProcess>
        </cac:ProcurementProjectLot>
    </root>
    """
    xml_file = tmp_path / "test_input_nonelectronic_submission_justification.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open('output.json', 'r') as f:
        result = json.load(f)

    assert "tender" in result
    assert "lots" in result["tender"]
    assert len(result["tender"]["lots"]) == 1
    lot = result["tender"]["lots"][0]
    assert lot["id"] == "LOT-0001"
    assert "submissionTerms" in lot
    assert "nonElectronicSubmission" in lot["submissionTerms"]
    assert lot["submissionTerms"]["nonElectronicSubmission"]["rationale"] == "Inclusion of a physical model"

if __name__ == "__main__":
    pytest.main()