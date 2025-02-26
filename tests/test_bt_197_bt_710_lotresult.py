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


def test_bt_197_bt710_lot_result_integration(
    tmp_path, setup_logging, temp_output_dir
) -> None:
    logger = setup_logging
    xml_content = """
    <ContractNotice xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
        xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
        xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
        xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
        xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
        xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1">
        <efac:noticeResult>
            <efac:LotResult>
                <efac:FieldsPrivacy>
                    <efbc:FieldIdentifierCode>ten-val-low</efbc:FieldIdentifierCode>
                    <cbc:ReasonCode listName="non-publication-justification">oth-int</cbc:ReasonCode>
                </efac:FieldsPrivacy>
                <cbc:ID schemeName="result">RES-0001</cbc:ID>
            </efac:LotResult>
        </efac:noticeResult>
    </ContractNotice>
    """

    xml_file = tmp_path / "test_input_bt197_bt710.xml"
    xml_file.write_text(xml_content)

    result = run_main_and_get_result(xml_file, temp_output_dir)
    # logger.info("Result: %s", json.dumps(result, indent=2) # Logging disabled)

    assert "withheldInformation" in result, "Expected 'withheldInformation' in result"
    assert (
        len(result["withheldInformation"]) == 1
    ), f"Expected 1 withheld information item, got {len(result['withheldInformation'])}"

    withheld_info = result["withheldInformation"][0]
    assert (
        withheld_info["id"] == "ten-val-low-RES-0001"
    ), "Unexpected withheld information id"
    assert (
        withheld_info["field"] == "ten-val-low"
    ), "Unexpected withheld information field"

    assert (
        "rationaleClassifications" in withheld_info
    ), "Expected 'rationaleClassifications' in withheld information"
    assert (
        len(withheld_info["rationaleClassifications"]) == 1
    ), "Expected 1 rationale classification"

    classification = withheld_info["rationaleClassifications"][0]
    assert (
        classification["scheme"] == "eu-non-publication-justification"
    ), "Unexpected classification scheme"
    assert classification["id"] == "oth-int", "Unexpected classification id"
    assert (
        classification["description"] == "Other public interest"
    ), "Unexpected classification description"
    assert (
        classification["uri"]
        == "http://publications.europa.eu/resource/authority/non-publication-justification/oth-int"
    ), "Unexpected classification uri"


def test_bt_197_bt710_lot_result_missing_field(
    tmp_path, setup_logging, temp_output_dir
) -> None:
    logger = setup_logging
    xml_content = """
    <ContractNotice xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
        xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
        xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
        xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
        xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
        xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1">
        <efac:noticeResult>
            <efac:LotResult>
                <cbc:ID schemeName="result">RES-0001</cbc:ID>
            </efac:LotResult>
        </efac:noticeResult>
    </ContractNotice>
    """

    xml_file = tmp_path / "test_input_bt197_bt710_missing.xml"
    xml_file.write_text(xml_content)

    result = run_main_and_get_result(xml_file, temp_output_dir)
    # logger.info("Result: %s", json.dumps(result, indent=2) # Logging disabled)

    assert (
        "withheldInformation" not in result
        or len(result.get("withheldInformation", [])) == 0
    ), "Did not expect 'withheldInformation' when FieldsPrivacy is missing"


if __name__ == "__main__":
    pytest.main(["-v", "-s"])
