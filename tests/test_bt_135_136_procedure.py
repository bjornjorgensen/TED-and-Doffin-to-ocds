# tests/test_bt_135_136_procedure.py
import json
import logging
import sys
import tempfile
from pathlib import Path

import pytest

# Add the parent directory to sys.path to import main
sys.path.append(str(Path(__file__).parent.parent))
from src.ted_and_doffin_to_ocds.main import configure_logging, main


@pytest.fixture(scope="module")
def setup_logging():
    # Logging disabled for tests
    logger = logging.getLogger(__name__)
    logger.disabled = True
    return logger


@pytest.fixture
def temp_output_dir():
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield Path(tmpdirname)


def run_main_and_get_result(xml_file, output_dir):
    main(str(xml_file), str(output_dir), "ocds-test-prefix", "test-scheme")
    output_files = list(output_dir.glob("*.json"))
    assert len(output_files) == 1, f"Expected 1 output file, got {len(output_files)}"
    with output_files[0].open() as f:
        return json.load(f)


def test_bt_135_136_procedure_integration(
    tmp_path, setup_logging, temp_output_dir
) -> None:
    logger = setup_logging

    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
        xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
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
    </ContractAwardNotice>
    """

    # Create input XML file
    xml_file = tmp_path / "test_input_direct_award_justification.xml"
    xml_file.write_text(xml_content)

    # Run main and get result
    result = run_main_and_get_result(xml_file, temp_output_dir)
    # logger.info("Result: %s", json.dumps(result, indent=2) # Logging disabled)

    # Verify the results
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
    pytest.main(["-v", "-s"])
