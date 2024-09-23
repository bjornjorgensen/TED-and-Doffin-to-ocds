# tests/test_bt_763_LotsAllRequired.py

import pytest
import json
import os
import sys
import logging

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.ted_and_doffin_to_ocds.main import main, configure_logging


@pytest.fixture(scope="module")
def setup_logging():
    configure_logging()
    return logging.getLogger(__name__)


def test_bt_763_lots_all_required_integration(tmp_path, setup_logging):
    logger = setup_logging

    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:TenderingProcess>
            <cbc:partPresentationCode listName="tenderlot-presentation">all</cbc:partPresentationCode>
        </cac:TenderingProcess>
    </root>
    """
    xml_file = tmp_path / "test_input_lots_all_required.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open("output.json") as f:
        result = json.load(f)

    logger.info(f"Result: {json.dumps(result, indent=2)}")

    assert "tender" in result, "Expected 'tender' in result"
    assert "lotDetails" in result["tender"], "Expected 'lotDetails' in tender"
    assert (
        "maximumLotsBidPerSupplier" in result["tender"]["lotDetails"]
    ), "Expected 'maximumLotsBidPerSupplier' in lotDetails"

    max_lots = result["tender"]["lotDetails"]["maximumLotsBidPerSupplier"]
    assert (
        max_lots == 1e9999
    ), f"Expected maximumLotsBidPerSupplier to be 1e9999, got {max_lots}"


def test_bt_763_lots_all_required_not_all(tmp_path, setup_logging):
    logger = setup_logging

    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:TenderingProcess>
            <cbc:partPresentationCode listName="tenderlot-presentation">some</cbc:partPresentationCode>
        </cac:TenderingProcess>
    </root>
    """
    xml_file = tmp_path / "test_input_lots_not_all_required.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open("output.json") as f:
        result = json.load(f)

    logger.info(f"Result: {json.dumps(result, indent=2)}")

    assert "tender" not in result or (
        "lotDetails" not in result.get("tender", {})
    ), "Did not expect 'lotDetails' in result when partPresentationCode is not 'all'"


def test_bt_763_lots_all_required_missing_element(tmp_path, setup_logging):
    logger = setup_logging

    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:TenderingProcess>
            <!-- partPresentationCode is missing -->
        </cac:TenderingProcess>
    </root>
    """
    xml_file = tmp_path / "test_input_lots_missing_element.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open("output.json") as f:
        result = json.load(f)

    logger.info(f"Result: {json.dumps(result, indent=2)}")

    assert "tender" not in result or (
        "lotDetails" not in result.get("tender", {})
    ), "Did not expect 'lotDetails' in result when partPresentationCode is missing"


def test_bt_763_lots_all_required_empty_value(tmp_path, setup_logging):
    logger = setup_logging

    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:TenderingProcess>
            <cbc:partPresentationCode listName="tenderlot-presentation"></cbc:partPresentationCode>
        </cac:TenderingProcess>
    </root>
    """
    xml_file = tmp_path / "test_input_lots_empty_value.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open("output.json") as f:
        result = json.load(f)

    logger.info(f"Result: {json.dumps(result, indent=2)}")

    assert "tender" not in result or (
        "lotDetails" not in result.get("tender", {})
    ), "Did not expect 'lotDetails' in result when partPresentationCode is empty"


def test_bt_763_lots_all_required_case_insensitive(tmp_path, setup_logging):
    logger = setup_logging

    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:TenderingProcess>
            <cbc:partPresentationCode listName="tenderlot-presentation">ALL</cbc:partPresentationCode>
        </cac:TenderingProcess>
    </root>
    """
    xml_file = tmp_path / "test_input_lots_case_insensitive.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open("output.json") as f:
        result = json.load(f)

    logger.info(f"Result: {json.dumps(result, indent=2)}")

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
