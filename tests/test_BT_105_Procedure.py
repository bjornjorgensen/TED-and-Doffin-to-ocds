# tests/test_BT_105_Procedure.py

import pytest
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main


@pytest.mark.parametrize(
    "procedure_code, expected_method, expected_details",
    [
        ("open", "open", "Open"),
        ("restricted", "selective", "Restricted"),
        ("comp-dial", "selective", "Competitive dialogue"),
        (
            "comp-tend",
            "selective",
            "Competitive tendering (article 5(3) of Regulation 1370/2007)",
        ),
        (
            "exp-int-rail",
            "selective",
            "Request for expression of interest – only for rail (article 5(3b) of Regulation 1370/2007)",
        ),
        ("innovation", "selective", "Innovation partnership"),
        (
            "neg-w-call",
            "selective",
            "Negotiated with prior publication of a call for competition / competitive with negotiation",
        ),
        ("neg-wo-call", "limited", "Negotiated without prior call for competition"),
        ("oth-mult", None, "Other multiple stage procedure"),
        ("oth-single", None, "Other single stage procedure"),
    ],
)
def test_bt_105_procedure_integration(
    tmp_path, procedure_code, expected_method, expected_details
):
    xml_content = f"""
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:TenderingProcess>
            <cbc:ProcedureCode listName="procurement-procedure-type">{procedure_code}</cbc:ProcedureCode>
        </cac:TenderingProcess>
    </root>
    """
    xml_file = tmp_path / f"test_input_procedure_type_{procedure_code}.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open("output.json") as f:
        result = json.load(f)

    assert "tender" in result, "Expected 'tender' in result"

    if expected_method:
        assert (
            "procurementMethod" in result["tender"]
        ), f"Expected 'procurementMethod' in tender for {procedure_code}"
        assert (
            result["tender"]["procurementMethod"] == expected_method
        ), f"Expected procurementMethod '{expected_method}', got {result['tender'].get('procurementMethod')}"
    else:
        assert (
            "procurementMethod" not in result["tender"]
        ), f"Unexpected 'procurementMethod' in tender for {procedure_code}"

    assert (
        "procurementMethodDetails" in result["tender"]
    ), f"Expected 'procurementMethodDetails' in tender for {procedure_code}"
    assert (
        result["tender"]["procurementMethodDetails"] == expected_details
    ), f"Expected procurementMethodDetails '{expected_details}', got {result['tender']['procurementMethodDetails']}"


if __name__ == "__main__":
    pytest.main()
