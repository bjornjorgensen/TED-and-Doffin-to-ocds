# tests/test_BT_106_Procedure.py

import pytest
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.ted_and_doffin_to_ocds.main import main


@pytest.mark.parametrize(
    ("accelerated_value", "expected_result"),
    [
        ("true", True),
        ("false", False),
        ("True", True),
        ("False", False),
    ],
)
def test_bt_106_procedure_integration(tmp_path, accelerated_value, expected_result):
    xml_content = f"""
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:TenderingProcess>
            <cac:ProcessJustification>
                <cbc:ProcessReasonCode listName="accelerated-procedure">{accelerated_value}</cbc:ProcessReasonCode>
            </cac:ProcessJustification>
        </cac:TenderingProcess>
    </root>
    """
    xml_file = tmp_path / f"test_input_procedure_accelerated_{accelerated_value}.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open("output.json") as f:
        result = json.load(f)

    assert "tender" in result, "Expected 'tender' in result"
    assert "procedure" in result["tender"], "Expected 'procedure' in tender"
    assert (
        "isAccelerated" in result["tender"]["procedure"]
    ), "Expected 'isAccelerated' in tender.procedure"
    assert (
        result["tender"]["procedure"]["isAccelerated"] == expected_result
    ), f"Expected isAccelerated to be {expected_result}, got {result['tender']['procedure']['isAccelerated']}"


def test_bt_106_procedure_integration_missing(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:TenderingProcess>
        </cac:TenderingProcess>
    </root>
    """
    xml_file = tmp_path / "test_input_procedure_accelerated_missing.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open("output.json") as f:
        result = json.load(f)

    assert "tender" not in result or "procedure" not in result.get(
        "tender", {}
    ), "Unexpected 'tender' or 'procedure' in result when missing in input"


if __name__ == "__main__":
    pytest.main()
