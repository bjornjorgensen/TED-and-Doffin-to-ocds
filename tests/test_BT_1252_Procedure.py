# tests/test_BT_1252_Procedure.py

import pytest
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main


def test_bt_1252_procedure_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:TenderingProcess>
            <cac:ProcessJustification>
                <cbc:ProcessReasonCode listName="direct-award-justification">irregular</cbc:ProcessReasonCode>
                <cbc:Description>123e4567-e89b-12d3-a456-426614174000</cbc:Description>
            </cac:ProcessJustification>
        </cac:TenderingProcess>
        <cac:TenderingProcess>
            <cac:ProcessJustification>
                <cbc:ProcessReasonCode listName="direct-award-justification">additional</cbc:ProcessReasonCode>
                <cbc:Description>234e5678-e89b-12d3-a456-426614174000</cbc:Description>
            </cac:ProcessJustification>
        </cac:TenderingProcess>
    </root>
    """
    xml_file = tmp_path / "test_input_direct_award_justification.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open("output.json", "r") as f:
        result = json.load(f)

    assert "relatedProcesses" in result, "Expected 'relatedProcesses' in result"
    assert (
        len(result["relatedProcesses"]) == 2
    ), f"Expected 2 related processes, got {len(result['relatedProcesses'])}"

    process_1 = result["relatedProcesses"][0]
    assert process_1["id"] == "1", "Expected first process id to be '1'"
    assert (
        process_1["identifier"] == "123e4567-e89b-12d3-a456-426614174000"
    ), "Unexpected identifier for first process"
    assert process_1["scheme"] == "eu-oj", "Expected scheme to be 'eu-oj'"
    assert (
        "unsuccessfulProcess" in process_1["relationship"]
    ), "Expected 'unsuccessfulProcess' in relationship for irregular code"

    process_2 = result["relatedProcesses"][1]
    assert process_2["id"] == "2", "Expected second process id to be '2'"
    assert (
        process_2["identifier"] == "234e5678-e89b-12d3-a456-426614174000"
    ), "Unexpected identifier for second process"
    assert process_2["scheme"] == "eu-oj", "Expected scheme to be 'eu-oj'"
    assert (
        "prior" in process_2["relationship"]
    ), "Expected 'prior' in relationship for additional code"


if __name__ == "__main__":
    pytest.main()
