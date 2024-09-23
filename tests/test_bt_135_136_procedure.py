# tests/test_bt_135_136_procedure.py

import pytest
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.ted_and_doffin_to_ocds.main import main


def test_bt_135_136_procedure_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:TenderingProcess>
            <cac:ProcessJustification>
                <cbc:ProcessReasonCode listName="direct-award-justification">ecom-excl</cbc:ProcessReasonCode>
                <cbc:ProcessReason>Specific exclusion justification text</cbc:ProcessReason>
            </cac:ProcessJustification>
            <cac:ProcessJustification>
                <cbc:ProcessReasonCode listName="direct-award-justification">technical</cbc:ProcessReasonCode>
                <cbc:ProcessReason>Technical reasons justification text</cbc:ProcessReason>
            </cac:ProcessJustification>
        </cac:TenderingProcess>
    </root>
    """
    xml_file = tmp_path / "test_input_direct_award_justification.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open("output.json") as f:
        result = json.load(f)

    assert "tender" in result, "Expected 'tender' in result"

    # Check BT-135: procurementMethodRationale
    assert (
        "procurementMethodRationale" in result["tender"]
    ), "Expected 'procurementMethodRationale' in tender"
    expected_rationale = (
        "Specific exclusion justification text Technical reasons justification text"
    )
    assert (
        result["tender"]["procurementMethodRationale"] == expected_rationale
    ), "Unexpected procurementMethodRationale"

    # Check BT-136: procurementMethodRationaleClassifications
    assert (
        "procurementMethodRationaleClassifications" in result["tender"]
    ), "Expected 'procurementMethodRationaleClassifications' in tender"
    classifications = result["tender"]["procurementMethodRationaleClassifications"]
    assert len(classifications) == 2, "Expected two classifications"

    assert (
        classifications[0]["scheme"] == "eu-direct-award-justification"
    ), "Unexpected scheme"
    assert classifications[0]["id"] == "ecom-excl", "Unexpected id"
    assert (
        classifications[0]["description"]
        == "Specific exclusion in the field of electronic communications"
    ), "Unexpected description"

    assert (
        classifications[1]["scheme"] == "eu-direct-award-justification"
    ), "Unexpected scheme"
    assert classifications[1]["id"] == "technical", "Unexpected id"
    assert (
        classifications[1]["description"]
        == "The contract can be provided only by a particular economic operator because of an absence of competition for technical reasons"
    ), "Unexpected description"


if __name__ == "__main__":
    pytest.main()
