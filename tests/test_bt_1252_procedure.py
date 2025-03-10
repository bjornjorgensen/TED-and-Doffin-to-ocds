# tests/test_bt_1252_procedure.py
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


def test_bt_1252_procedure_integration(
    tmp_path, setup_logging, temp_output_dir
) -> None:
    logger = setup_logging

    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
        xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
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
    </ContractAwardNotice>
    """

    # Create input XML file
    xml_file = tmp_path / "test_input_direct_award_justification.xml"
    xml_file.write_text(xml_content)

    # Run main and get result
    result = run_main_and_get_result(xml_file, temp_output_dir)
    # logger.info("Result: %s", json.dumps(result, indent=2) # Logging disabled)

    # Verify the results
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
    pytest.main(["-v", "-s"])
