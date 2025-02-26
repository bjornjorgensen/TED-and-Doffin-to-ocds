# tests/test_bt_763_LotsAllRequired.py
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


def test_bt_763_lots_all_required_integration(
    tmp_path, setup_logging, temp_output_dir
) -> None:
    logger = setup_logging
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<ContractNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractNotice-2"
    xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
    xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
    <cac:TenderingProcess>
        <cbc:partPresentationCode listName="tenderlot-presentation">all</cbc:partPresentationCode>
    </cac:TenderingProcess>
</ContractNotice>
    """
    xml_file = tmp_path / "test_input_lots_all_required.xml"
    xml_file.write_text(xml_content)

    result = run_main_and_get_result(xml_file, temp_output_dir)

    # logger.info("Result: %s", json.dumps(result, indent=2) # Logging disabled)

    assert "tender" in result, "Expected 'tender' in result"
    assert "lotDetails" in result["tender"], "Expected 'lotDetails' in tender"
    assert (
        "maximumLotsBidPerSupplier" in result["tender"]["lotDetails"]
    ), "Expected 'maximumLotsBidPerSupplier' in lotDetails"

    max_lots = result["tender"]["lotDetails"]["maximumLotsBidPerSupplier"]
    assert (
        max_lots == 1e9999
    ), f"Expected maximumLotsBidPerSupplier to be 1e9999, got {max_lots}"


def test_bt_763_lots_all_required_not_all(
    tmp_path, setup_logging, temp_output_dir
) -> None:
    logger = setup_logging
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<ContractNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractNotice-2"
    xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
    xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
    <cac:TenderingProcess>
        <cbc:partPresentationCode listName="tenderlot-presentation">some</cbc:partPresentationCode>
    </cac:TenderingProcess>
</ContractNotice>
    """
    xml_file = tmp_path / "test_input_lots_not_all_required.xml"
    xml_file.write_text(xml_content)

    result = run_main_and_get_result(xml_file, temp_output_dir)

    # logger.info("Result: %s", json.dumps(result, indent=2) # Logging disabled)

    assert "tender" not in result or (
        "lotDetails" not in result.get("tender", {})
    ), "Did not expect 'lotDetails' in result when partPresentationCode is not 'all'"


def test_bt_763_lots_all_required_missing_element(
    tmp_path, setup_logging, temp_output_dir
) -> None:
    logger = setup_logging
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<ContractNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractNotice-2"
    xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
    xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
    <cac:TenderingProcess>
        <!-- partPresentationCode is missing -->
    </cac:TenderingProcess>
</ContractNotice>
    """
    xml_file = tmp_path / "test_input_lots_missing_element.xml"
    xml_file.write_text(xml_content)

    result = run_main_and_get_result(xml_file, temp_output_dir)

    # logger.info("Result: %s", json.dumps(result, indent=2) # Logging disabled)

    assert "tender" not in result or (
        "lotDetails" not in result.get("tender", {})
    ), "Did not expect 'lotDetails' in result when partPresentationCode is missing"


def test_bt_763_lots_all_required_empty_value(
    tmp_path, setup_logging, temp_output_dir
) -> None:
    logger = setup_logging
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<ContractNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractNotice-2"
    xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
    xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
    <cac:TenderingProcess>
        <cbc:partPresentationCode listName="tenderlot-presentation"></cbc:partPresentationCode>
    </cac:TenderingProcess>
</ContractNotice>
    """
    xml_file = tmp_path / "test_input_lots_empty_value.xml"
    xml_file.write_text(xml_content)

    result = run_main_and_get_result(xml_file, temp_output_dir)

    # logger.info("Result: %s", json.dumps(result, indent=2) # Logging disabled)

    assert "tender" not in result or (
        "lotDetails" not in result.get("tender", {})
    ), "Did not expect 'lotDetails' in result when partPresentationCode is empty"


def test_bt_763_lots_all_required_case_insensitive(
    tmp_path, setup_logging, temp_output_dir
) -> None:
    logger = setup_logging
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<ContractNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractNotice-2"
    xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
    xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
    <cac:TenderingProcess>
        <cbc:partPresentationCode listName="tenderlot-presentation">ALL</cbc:partPresentationCode>
    </cac:TenderingProcess>
</ContractNotice>
    """
    xml_file = tmp_path / "test_input_lots_case_insensitive.xml"
    xml_file.write_text(xml_content)

    result = run_main_and_get_result(xml_file, temp_output_dir)

    # logger.info("Result: %s", json.dumps(result, indent=2) # Logging disabled)

    assert "tender" in result, "Expected 'tender' in result"
    assert "lotDetails" in result["tender"], "Expected 'lotDetails' in tender"
    assert (
        "maximumLotsBidPerSupplier" in result["tender"]["lotDetails"]
    ), "Expected 'maximumLotsBidPerSupplier' in lotDetails"

    max_lots = result["tender"]["lotDetails"]["maximumLotsBidPerSupplier"]
    assert (
        max_lots == 1e9999
    ), f"Expected maximumLotsBidPerSupplier to be 1e9999, got {max_lots}"


if __name__ == "__main__":
    pytest.main(["-v", "-s"])
