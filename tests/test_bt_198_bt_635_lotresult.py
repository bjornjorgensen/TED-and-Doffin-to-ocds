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


def test_bt_198_bt635_lotresult_integration(
    tmp_path, setup_logging, temp_output_dir
) -> None:
    logger = setup_logging
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractNotice xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
        xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
        xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
        xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
        xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
        xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1">
        <efac:NoticeResult>
            <efac:LotResult>
                <cbc:ID schemeName="result">RES-0001</cbc:ID>
                <efac:AppealRequestsStatistics>
                    <efbc:StatisticsCode listName="irregularity-type">total</efbc:StatisticsCode>
                    <efac:FieldsPrivacy>
                        <efbc:FieldIdentifierCode>buy-rev-cou</efbc:FieldIdentifierCode>
                        <efbc:PublicationDate>2025-03-31+01:00</efbc:PublicationDate>
                    </efac:FieldsPrivacy>
                </efac:AppealRequestsStatistics>
            </efac:LotResult>
        </efac:NoticeResult>
    </ContractNotice>
    """
    xml_file = tmp_path / "test_input_bt198_bt635.xml"
    xml_file.write_text(xml_content)

    result = run_main_and_get_result(xml_file, temp_output_dir)

    # logger.info("Result: %s", json.dumps(result, indent=2) # Logging disabled)

    assert "withheldInformation" in result, "Expected 'withheldInformation' in result"
    withheld_info = result["withheldInformation"]
    assert (
        len(withheld_info) == 1
    ), f"Expected 1 withheld information item, got {len(withheld_info)}"

    item = withheld_info[0]
    assert (
        item["id"] == "buy-rev-cou-RES-0001"
    ), f"Expected id 'buy-rev-cou-RES-0001', got {item['id']}"
    assert (
        "availabilityDate" in item
    ), "Expected 'availabilityDate' in withheld information item"
    assert (
        item["availabilityDate"] == "2025-03-31T00:00:00+01:00"
    ), f"Unexpected availabilityDate: {item['availabilityDate']}"


if __name__ == "__main__":
    pytest.main(["-v", "-s"])
