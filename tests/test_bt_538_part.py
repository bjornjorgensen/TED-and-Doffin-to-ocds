# tests/test_bt_538_part.py
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
    output_files = list(output_dir.glob("*_release_0.json"))
    assert len(output_files) == 1, f"Expected 1 output file, got {len(output_files)}"
    with output_files[0].open() as f:
        return json.load(f)


def test_bt_538_part_integration(tmp_path, setup_logging, temp_output_dir) -> None:
    logger = setup_logging

    xml_content = """
    <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
                          xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
                          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cbc:ID>notice-538</cbc:ID>
        <cbc:ContractFolderID>cf-538</cbc:ContractFolderID>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Part">PART-0001</cbc:ID>
            <cac:ProcurementProject>
                <cac:PlannedPeriod>
                    <cbc:DescriptionCode listName="timeperiod">UNLIMITED</cbc:DescriptionCode>
                </cac:PlannedPeriod>
            </cac:ProcurementProject>
        </cac:ProcurementProjectLot>
    </ContractAwardNotice>
    """
    xml_file = tmp_path / "test_input_part_duration_other.xml"
    xml_file.write_text(xml_content)

    # Run main and get result
    result = run_main_and_get_result(xml_file, temp_output_dir)

    # logger.info("Result: %s", json.dumps(result, indent=2) # Logging disabled)

    # Assertions
    assert "tender" in result, "Expected 'tender' in result"
    assert "contractPeriod" in result["tender"], "Expected 'contractPeriod' in tender"
    assert (
        "description" in result["tender"]["contractPeriod"]
    ), "Expected 'description' in tender contractPeriod"
    expected_description = "UNLIMITED"
    assert (
        result["tender"]["contractPeriod"]["description"] == expected_description
    ), f"Expected description '{expected_description}', got {result['tender']['contractPeriod']['description']}"

    # logger.info("Test bt_538_part_integration passed successfully.") # Logging disabled


if __name__ == "__main__":
    pytest.main(["-v", "-s"])
