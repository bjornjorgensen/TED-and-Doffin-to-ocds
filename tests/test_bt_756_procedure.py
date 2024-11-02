# tests/test_bt_756_procedure.py
from pathlib import Path
import pytest
import json
import sys
import tempfile
import logging

# Add the parent directory to sys.path to import main
sys.path.append(str(Path(__file__).parent.parent))
from src.ted_and_doffin_to_ocds.main import main, configure_logging


@pytest.fixture(scope="module")
def setup_logging():
    configure_logging()
    return logging.getLogger(__name__)


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


def test_bt_756_procedure_integration(tmp_path, setup_logging, temp_output_dir):
    logger = setup_logging

    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:TenderingProcess>
            <cbc:TerminatedIndicator>true</cbc:TerminatedIndicator>
        </cac:TenderingProcess>
    </root>
    """
    xml_file = tmp_path / "test_input_pin_competition_termination.xml"
    xml_file.write_text(xml_content)

    result = run_main_and_get_result(xml_file, temp_output_dir)
    logger.info("Result: %s", json.dumps(result, indent=2))

    assert "tender" in result, "Expected 'tender' in result"
    assert "status" in result["tender"], "Expected 'status' in tender"
    assert (
        result["tender"]["status"] == "complete"
    ), f"Expected tender status 'complete', got {result['tender']['status']}"


def test_bt_756_procedure_integration_false(tmp_path, setup_logging, temp_output_dir):
    logger = setup_logging

    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:TenderingProcess>
            <cbc:TerminatedIndicator>false</cbc:TerminatedIndicator>
        </cac:TenderingProcess>
    </root>
    """
    xml_file = tmp_path / "test_input_pin_competition_termination_false.xml"
    xml_file.write_text(xml_content)

    result = run_main_and_get_result(xml_file, temp_output_dir)
    logger.info("Result: %s", json.dumps(result, indent=2))

    assert "status" not in result.get(
        "tender",
        {},
    ), "Did not expect 'status' in tender when TerminatedIndicator is false"


if __name__ == "__main__":
    pytest.main(["-v", "-s"])
