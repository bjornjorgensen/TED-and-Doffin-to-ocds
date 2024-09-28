# tests/test_bt_136_procedure.py
from pathlib import Path
import pytest
import json
import sys

# Add the parent directory to sys.path to import main
sys.path.append(str(Path(__file__).parent.parent))
from src.ted_and_doffin_to_ocds.main import main


def test_bt_136_procedure_integration(tmp_path):
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

    with Path("output.json").open() as f:
        result = json.load(f)

    assert "tender" in result, "Expected 'tender' in result"
    assert (
        "procurementMethodRationaleClassifications" in result["tender"]
    ), "Expected 'procurementMethodRationaleClassifications' in tender"
    assert (
        len(result["tender"]["procurementMethodRationaleClassifications"]) == 2
    ), f"Expected 2 classifications, got {len(result['tender']['procurementMethodRationaleClassifications'])}"

    assert "relatedProcesses" in result, "Expected 'relatedProcesses' in result"
    assert (
        len(result["relatedProcesses"]) == 2
    ), f"Expected 2 related processes, got {len(result['relatedProcesses'])}"

    # Check classifications
    classifications = result["tender"]["procurementMethodRationaleClassifications"]
    assert any(
        c["id"] == "irregular" for c in classifications
    ), "Expected 'irregular' classification"
    assert any(
        c["id"] == "additional" for c in classifications
    ), "Expected 'additional' classification"

    # Check related processes
    related_processes = result["relatedProcesses"]
    assert any(
        rp["identifier"] == "123e4567-e89b-12d3-a456-426614174000"
        for rp in related_processes
    ), "Expected related process with identifier '123e4567-e89b-12d3-a456-426614174000'"
    assert any(
        rp["identifier"] == "234e5678-e89b-12d3-a456-426614174000"
        for rp in related_processes
    ), "Expected related process with identifier '234e5678-e89b-12d3-a456-426614174000'"


if __name__ == "__main__":
    pytest.main()
