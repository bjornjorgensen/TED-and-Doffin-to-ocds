# tests/test_bt_106_procedure.py

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
    # Clear the output directory before each run
    for file in output_dir.glob("*.json"):
        file.unlink()
    main(str(xml_file), str(output_dir), "ocds-test-prefix", "test-scheme")
    output_files = list(output_dir.glob("*.json"))
    assert len(output_files) == 1, f"Expected 1 output file, got {len(output_files)}"
    with output_files[0].open() as f:
        return json.load(f)


def test_bt_106_procedure_accelerated_true(
    tmp_path, setup_logging, temp_output_dir
) -> None:
    logger = setup_logging

    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
        xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
        xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cbc:ID>notice-1</cbc:ID>
        <cbc:ContractFolderID>cf-1</cbc:ContractFolderID>
        <cac:TenderingProcess>
            <cac:ProcessJustification>
                <cbc:ProcessReasonCode listName="accelerated-procedure">true</cbc:ProcessReasonCode>
            </cac:ProcessJustification>
        </cac:TenderingProcess>
    </ContractAwardNotice>
    """

    # Create input XML file
    xml_file = tmp_path / "test_input_procedure_accelerated_true.xml"
    xml_file.write_text(xml_content)

    # Run main and get result
    result = run_main_and_get_result(xml_file, temp_output_dir)

    # Verify the results
    assert "tender" in result
    assert "procedure" in result["tender"]
    assert "isAccelerated" in result["tender"]["procedure"]
    assert result["tender"]["procedure"]["isAccelerated"] is True
    
    # Verify that no acceleratedRationale is present since there's no ProcessReason element
    assert "acceleratedRationale" not in result["tender"]["procedure"]


def test_bt_106_procedure_accelerated_with_rationale(
    tmp_path, setup_logging, temp_output_dir
) -> None:
    logger = setup_logging

    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
        xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
        xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cbc:ID>notice-1</cbc:ID>
        <cbc:ContractFolderID>cf-1</cbc:ContractFolderID>
        <cac:TenderingProcess>
            <cac:ProcessJustification>
                <cbc:ProcessReasonCode listName="accelerated-procedure">true</cbc:ProcessReasonCode>
                <cbc:ProcessReason>Emergency procurement due to urgent need</cbc:ProcessReason>
            </cac:ProcessJustification>
        </cac:TenderingProcess>
    </ContractAwardNotice>
    """

    # Create input XML file
    xml_file = tmp_path / "test_input_procedure_accelerated_with_rationale.xml"
    xml_file.write_text(xml_content)

    # Run main and get result
    result = run_main_and_get_result(xml_file, temp_output_dir)

    # Verify the results
    assert "tender" in result
    assert "procedure" in result["tender"]
    assert "isAccelerated" in result["tender"]["procedure"]
    assert result["tender"]["procedure"]["isAccelerated"] is True
    
    # Verify the accelerated rationale is present and correctly mapped
    assert "acceleratedRationale" in result["tender"]["procedure"]
    assert result["tender"]["procedure"]["acceleratedRationale"] == "Emergency procurement due to urgent need"


def test_bt_106_procedure_accelerated_alternative_values(
    tmp_path, setup_logging, temp_output_dir
) -> None:
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
        # Edge cases from spec
        ("", False),  # Empty value should default to false
        (None, False),  # Missing value should default to false
    ]

    for value, expected in test_cases:
        if value is None:
            xml_content = """<?xml version="1.0" encoding="UTF-8"?>
            <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
                xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
                xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
                <cbc:ID>notice-1</cbc:ID>
                <cbc:ContractFolderID>cf-1</cbc:ContractFolderID>
                <cac:TenderingProcess>
                    <cac:ProcessJustification>
                    </cac:ProcessJustification>
                </cac:TenderingProcess>
            </ContractAwardNotice>
            """
        else:
            xml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
            <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
                xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
                xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
                <cbc:ID>notice-1</cbc:ID>
                <cbc:ContractFolderID>cf-1</cbc:ContractFolderID>
                <cac:TenderingProcess>
                    <cac:ProcessJustification>
                        <cbc:ProcessReasonCode listName="accelerated-procedure">{value}</cbc:ProcessReasonCode>
                    </cac:ProcessJustification>
                </cac:TenderingProcess>
            </ContractAwardNotice>
            """

        # Create a new subdirectory for each test case
        case_dir = tmp_path / f"case_{value if value is not None else 'none'}"
        case_dir.mkdir(exist_ok=True)

        xml_file = case_dir / "test_input.xml"
        xml_file.write_text(xml_content)

        result = run_main_and_get_result(xml_file, temp_output_dir)

        if expected:
            assert "tender" in result, f"Missing tender for value: {value}"
            assert "procedure" in result["tender"], f"Missing procedure for value: {value}"
            assert "isAccelerated" in result["tender"]["procedure"], f"Missing isAccelerated for value: {value}"
            assert result["tender"]["procedure"]["isAccelerated"] is expected, f"Expected {expected} for value '{value}', got {result['tender']['procedure']['isAccelerated']}"
        else:
            # For false cases, tender.procedure might not exist at all, which is acceptable
            if "tender" in result and "procedure" in result["tender"]:
                if "isAccelerated" in result["tender"]["procedure"]:
                    assert result["tender"]["procedure"]["isAccelerated"] is False, f"Expected False for value '{value}', got {result['tender']['procedure']['isAccelerated']}"

        # Check rationale only if procedure exists
        if "tender" in result and "procedure" in result["tender"]:
            assert "acceleratedRationale" not in result["tender"]["procedure"], f"acceleratedRationale should not be present for value: {value}"


def test_bt_106_procedure_accelerated_alternative_values_with_rationale(
    tmp_path, setup_logging, temp_output_dir
) -> None:
    logger = setup_logging

    test_cases = [
        # (value, expected_result, rationale)
        ("1", True, "Urgency due to unforeseen circumstances"),
        ("yes", True, "Critical timeline requirements"),
        ("0", False, None),  # No rationale for false cases
        ("no", False, None),  # No rationale for false cases
    ]

    for value, expected, rationale in test_cases:
        # Create a new subdirectory for each test case
        case_dir = tmp_path / f"case_{value}_with_rationale"
        case_dir.mkdir(exist_ok=True)

        # Only include ProcessReason element if rationale is provided
        process_reason_element = f'<cbc:ProcessReason>{rationale}</cbc:ProcessReason>' if rationale else ''
        
        xml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
        <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
            xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
            xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
            <cbc:ID>notice-1</cbc:ID>
            <cbc:ContractFolderID>cf-1</cbc:ContractFolderID>
            <cac:TenderingProcess>
                <cac:ProcessJustification>
                    <cbc:ProcessReasonCode listName="accelerated-procedure">{value}</cbc:ProcessReasonCode>
                    {process_reason_element}
                </cac:ProcessJustification>
            </cac:TenderingProcess>
        </ContractAwardNotice>
        """

        xml_file = case_dir / "test_input.xml"
        xml_file.write_text(xml_content)

        result = run_main_and_get_result(xml_file, temp_output_dir)

        assert "tender" in result, f"Missing tender for value: {value}"
        assert "procedure" in result["tender"], f"Missing procedure for value: {value}"
        assert (
            "isAccelerated" in result["tender"]["procedure"]
        ), f"Missing isAccelerated for value: {value}"
        assert (
            result["tender"]["procedure"]["isAccelerated"] is expected
        ), f"Expected {expected} for value '{value}', got {result['tender']['procedure']['isAccelerated']}"
        
        if expected:
            assert "acceleratedRationale" in result["tender"]["procedure"], f"Missing acceleratedRationale for value: {value}"
            assert result["tender"]["procedure"]["acceleratedRationale"] == rationale, f"Expected acceleratedRationale '{rationale}' for value '{value}', got {result['tender']['procedure']['acceleratedRationale']}"
        else:
            # For non-accelerated cases, rationale should not be present
            assert "acceleratedRationale" not in result["tender"]["procedure"], f"acceleratedRationale should not be present for non-accelerated case: {value}"


def test_bt_106_procedure_accelerated_invalid_value(
    tmp_path, setup_logging, temp_output_dir
) -> None:
    logger = setup_logging

    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
        xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
        xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cbc:ID>notice-1</cbc:ID>
        <cbc:ContractFolderID>cf-1</cbc:ContractFolderID>
        <cac:TenderingProcess>
            <cac:ProcessJustification>
                <cbc:ProcessReasonCode listName="accelerated-procedure">invalid</cbc:ProcessReasonCode>
            </cac:ProcessJustification>
        </cac:TenderingProcess>
    </ContractAwardNotice>
    """

    xml_file = tmp_path / "test_input_procedure_accelerated_invalid.xml"
    xml_file.write_text(xml_content)

    result = run_main_and_get_result(xml_file, temp_output_dir)

    assert (
        "tender" not in result
        or "procedure" not in result.get("tender", {})
        or "isAccelerated" not in result.get("tender", {}).get("procedure", {})
    ), "Invalid value should not result in isAccelerated field"


def test_bt_106_procedure_accelerated_missing_element(
    tmp_path, setup_logging, temp_output_dir
) -> None:
    logger = setup_logging

    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
        xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
        xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cbc:ID>notice-1</cbc:ID>
        <cbc:ContractFolderID>cf-1</cbc:ContractFolderID>
        <cac:TenderingProcess>
            <cac:ProcessJustification>
                <!-- ProcessReasonCode is missing -->
            </cac:ProcessJustification>
        </cac:TenderingProcess>
    </ContractAwardNotice>
    """

    xml_file = tmp_path / "test_input_procedure_accelerated_missing.xml"
    xml_file.write_text(xml_content)

    result = run_main_and_get_result(xml_file, temp_output_dir)

    # logger.info("Result: %s", json.dumps(result, indent=2) # Logging disabled)

    assert (
        "tender" not in result
        or "procedure" not in result.get("tender", {})
        or "isAccelerated" not in result.get("tender", {}).get("procedure", {})
    )


def test_bt_106_different_notice_types(
    tmp_path, setup_logging, temp_output_dir
) -> None:
    logger = setup_logging

    notice_types = [
        ("ContractNotice", "CN"),
        ("ContractAwardNotice", "CAN")
    ]

    for root_element, notice_type in notice_types:
        xml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
        <{root_element} xmlns="urn:oasis:names:specification:ubl:schema:xsd:{root_element}-2"
            xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
            xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
            <cbc:ID>notice-1</cbc:ID>
            <cbc:ContractFolderID>cf-1</cbc:ContractFolderID>
            <cac:TenderingProcess>
                <cac:ProcessJustification>
                    <cbc:ProcessReasonCode listName="accelerated-procedure">true</cbc:ProcessReasonCode>
                    <cbc:ProcessReason>Test rationale for {notice_type}</cbc:ProcessReason>
                </cac:ProcessJustification>
            </cac:TenderingProcess>
        </{root_element}>
        """

        xml_file = tmp_path / f"test_input_{notice_type.lower()}.xml"
        xml_file.write_text(xml_content)

        result = run_main_and_get_result(xml_file, temp_output_dir)

        # Both notice types should support accelerated procedure
        assert "tender" in result, f"Missing tender for notice type: {notice_type}"
        assert "procedure" in result["tender"], f"Missing procedure for notice type: {notice_type}"
        assert "isAccelerated" in result["tender"]["procedure"], f"Missing isAccelerated for notice type: {notice_type}"
        assert result["tender"]["procedure"]["isAccelerated"] is True, f"Expected True for notice type {notice_type}"
        assert "acceleratedRationale" in result["tender"]["procedure"], f"Missing acceleratedRationale for notice type: {notice_type}"
        assert result["tender"]["procedure"]["acceleratedRationale"] == f"Test rationale for {notice_type}", f"Wrong rationale for notice type: {notice_type}"


if __name__ == "__main__":
    pytest.main(["-v", "-s"])
