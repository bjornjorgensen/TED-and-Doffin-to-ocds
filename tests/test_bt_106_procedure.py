# tests/test_bt_106_procedure.py

from pathlib import Path
import pytest
import json
import sys
import logging
import tempfile

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
    # Clear the output directory before each run
    for file in output_dir.glob("*.json"):
        file.unlink()

    main(str(xml_file), str(output_dir), "ocds-test-prefix", "test-scheme")
    output_files = list(output_dir.glob("*.json"))
    assert len(output_files) == 1, f"Expected 1 output file, got {len(output_files)}"
    with output_files[0].open() as f:
        return json.load(f)


def test_bt_106_procedure_accelerated_true(tmp_path, setup_logging, temp_output_dir):
    logger = setup_logging
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:TenderingProcess>
            <cac:ProcessJustification>
                <cbc:ProcessReasonCode listName="accelerated-procedure">true</cbc:ProcessReasonCode>
            </cac:ProcessJustification>
        </cac:TenderingProcess>
    </root>
    """
    xml_file = tmp_path / "test_input_procedure_accelerated_true.xml"
    xml_file.write_text(xml_content)

    result = run_main_and_get_result(xml_file, temp_output_dir)
    logger.info("Result: %s", json.dumps(result, indent=2))

    assert "tender" in result
    assert "procedure" in result["tender"]
    assert "isAccelerated" in result["tender"]["procedure"]
    assert result["tender"]["procedure"]["isAccelerated"] is True


def test_bt_106_procedure_accelerated_alternative_values(
    tmp_path, setup_logging, temp_output_dir
):
    logger = setup_logging
    test_cases = [
        # (value, expected_result)
        ("1", True),
        ("yes", True),
        ("TRUE", True),
        (" true ", True),
        ("Yes", True),
        ("0", False),
        ("no", False),
        ("FALSE", False),
        (" false ", False),
        ("No", False),
    ]

    for value, expected in test_cases:
        # Create a new subdirectory for each test case
        case_dir = tmp_path / f"case_{value}"
        case_dir.mkdir(exist_ok=True)

        xml_content = f"""
        <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
              xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
            <cac:TenderingProcess>
                <cac:ProcessJustification>
                    <cbc:ProcessReasonCode listName="accelerated-procedure">{value}</cbc:ProcessReasonCode>
                </cac:ProcessJustification>
            </cac:TenderingProcess>
        </root>
        """
        xml_file = case_dir / "test_input.xml"
        xml_file.write_text(xml_content)

        result = run_main_and_get_result(xml_file, temp_output_dir)
        logger.info("Result for value '%s': %s", value, json.dumps(result, indent=2))

        assert "tender" in result, f"Missing tender for value: {value}"
        assert "procedure" in result["tender"], f"Missing procedure for value: {value}"
        assert (
            "isAccelerated" in result["tender"]["procedure"]
        ), f"Missing isAccelerated for value: {value}"
        assert (
            result["tender"]["procedure"]["isAccelerated"] is expected
        ), f"Expected {expected} for value '{value}', got {result['tender']['procedure']['isAccelerated']}"


def test_bt_106_procedure_accelerated_invalid_value(
    tmp_path, setup_logging, temp_output_dir
):
    logger = setup_logging
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:TenderingProcess>
            <cac:ProcessJustification>
                <cbc:ProcessReasonCode listName="accelerated-procedure">invalid</cbc:ProcessReasonCode>
            </cac:ProcessJustification>
        </cac:TenderingProcess>
    </root>
    """
    xml_file = tmp_path / "test_input_procedure_accelerated_invalid.xml"
    xml_file.write_text(xml_content)

    result = run_main_and_get_result(xml_file, temp_output_dir)
    logger.info("Result: %s", json.dumps(result, indent=2))

    assert (
        "tender" not in result
        or "procedure" not in result.get("tender", {})
        or "isAccelerated" not in result.get("tender", {}).get("procedure", {})
    ), "Invalid value should not result in isAccelerated field"


def test_bt_106_procedure_accelerated_missing_element(
    tmp_path, setup_logging, temp_output_dir
):
    logger = setup_logging
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:TenderingProcess>
            <cac:ProcessJustification>
                <!-- ProcessReasonCode is missing -->
            </cac:ProcessJustification>
        </cac:TenderingProcess>
    </root>
    """
    xml_file = tmp_path / "test_input_procedure_accelerated_missing.xml"
    xml_file.write_text(xml_content)

    result = run_main_and_get_result(xml_file, temp_output_dir)
    logger.info("Result: %s", json.dumps(result, indent=2))

    assert (
        "tender" not in result
        or "procedure" not in result.get("tender", {})
        or "isAccelerated" not in result.get("tender", {}).get("procedure", {})
    )


if __name__ == "__main__":
    pytest.main(["-v", "-s"])
