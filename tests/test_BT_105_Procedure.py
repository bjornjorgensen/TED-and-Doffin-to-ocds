# tests/test_BT_105_Procedure.py

import pytest
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main


def create_xml_with_procedure_code(procedure_code):
    return f"""
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:TenderingProcess>
            <cbc:ProcedureCode listName="procurement-procedure-type">{procedure_code}</cbc:ProcedureCode>
        </cac:TenderingProcess>
    </root>
    """


@pytest.mark.parametrize(
    ("procedure_code", "expected_method", "expected_details"),
    [
        ("open", "open", "Open procedure"),
        ("restricted", "selective", "Restricted procedure"),
        ("comp-dial", "selective", "Competitive dialogue"),
        (
            "comp-tend",
            "selective",
            "Competitive tendering (article 5(3) of Regulation 1370/2007)",
        ),
        ("innovation", "selective", "Innovation partnership"),
        (
            "neg-w-call",
            "selective",
            "Negotiated with prior publication of a call for competition / competitive with negotiation",
        ),
        ("neg-wo-call", "limited", "Negotiated without prior call for competition"),
        (
            "exp-int-rail",
            "selective",
            "Request for expression of interest – only for rail (article 5(3b) of Regulation 1370/2007)",
        ),
        ("oth-mult", None, "Other multiple stage procedure"),
        ("oth-single", None, "Other single stage procedure"),
    ],
)
def test_bt_105_procedure_integration(
    tmp_path, procedure_code, expected_method, expected_details
):
    xml_content = create_xml_with_procedure_code(procedure_code)
    xml_file = tmp_path / f"test_input_procedure_{procedure_code}.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open("output.json") as f:
        result = json.load(f)

    assert "tender" in result, "Expected 'tender' in result"
    assert (
        "procurementMethodDetails" in result["tender"]
    ), "Expected 'procurementMethodDetails' in tender"
    assert (
        result["tender"]["procurementMethodDetails"] == expected_details
    ), f"Expected procurementMethodDetails '{expected_details}', got '{result['tender']['procurementMethodDetails']}'"

    if expected_method:
        assert (
            "procurementMethod" in result["tender"]
        ), "Expected 'procurementMethod' in tender"
        assert (
            result["tender"]["procurementMethod"] == expected_method
        ), f"Expected procurementMethod '{expected_method}', got '{result['tender']['procurementMethod']}'"
    else:
        assert (
            "procurementMethod" not in result["tender"]
        ), f"Did not expect 'procurementMethod' in tender for procedure code '{procedure_code}'"


def test_bt_105_procedure_missing_code(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:TenderingProcess>
            <!-- ProcedureCode is missing -->
        </cac:TenderingProcess>
    </root>
    """
    xml_file = tmp_path / "test_input_missing_procedure_code.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open("output.json") as f:
        result = json.load(f)

    assert (
        "tender" not in result or "procurementMethod" not in result["tender"]
    ), "Did not expect 'procurementMethod' when ProcedureCode is missing"
    assert (
        "tender" not in result or "procurementMethodDetails" not in result["tender"]
    ), "Did not expect 'procurementMethodDetails' when ProcedureCode is missing"


if __name__ == "__main__":
    pytest.main()
