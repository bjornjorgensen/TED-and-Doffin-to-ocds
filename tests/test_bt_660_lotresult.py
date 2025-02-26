# tests/test_bt_660_lotresult.py

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


def test_bt_660_lotresult_integration(tmp_path, setup_logging, temp_output_dir) -> None:
    logger = setup_logging
    xml_content = """
    <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
                          xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
                          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
                          xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
                          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
                          xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
                          xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1">
        <efac:NoticeResult>
            <efac:LotResult>
                <efac:AppealRequestsStatistics>
                    <efbc:StatisticsCode listName="irregularity-type">unj-lim-subc</efbc:StatisticsCode>
                    <efbc:StatisticsNumeric>2</efbc:StatisticsNumeric>
                </efac:AppealRequestsStatistics>
                <efac:TenderLot>
                    <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
                </efac:TenderLot>
            </efac:LotResult>
            <efac:LotResult>
                <efac:AppealRequestsStatistics>
                    <efbc:StatisticsCode listName="irregularity-type">ab-low</efbc:StatisticsCode>
                    <efbc:StatisticsNumeric>3</efbc:StatisticsNumeric>
                </efac:AppealRequestsStatistics>
                <efac:TenderLot>
                    <cbc:ID schemeName="Lot">LOT-0002</cbc:ID>
                </efac:TenderLot>
            </efac:LotResult>
        </efac:NoticeResult>
    </ContractAwardNotice>
    """
    xml_file = tmp_path / "test_input_buyer_review_requests_irregularity_type.xml"
    xml_file.write_text(xml_content)

    # Run main and get result
    result = run_main_and_get_result(xml_file, temp_output_dir)

    # logger.info("Result: %s", json.dumps(result, indent=2) # Logging disabled)

    assert "statistics" in result, "Expected 'statistics' in result"
    assert (
        len(result["statistics"]) == 2
    ), f"Expected 2 statistics, got {len(result['statistics'])}"

    lot1_statistic = next(
        (stat for stat in result["statistics"] if stat["relatedLot"] == "LOT-0001"),
        None,
    )
    assert lot1_statistic is not None, "Expected statistic for LOT-0001"
    assert (
        lot1_statistic["measure"] == "unj-lim-subc"
    ), f"Expected measure 'unj-lim-subc' for LOT-0001, got {lot1_statistic['measure']}"
    assert (
        lot1_statistic["notes"] == "Unjustified limitation of subcontracting"
    ), f"Expected notes 'Unjustified limitation of subcontracting' for LOT-0001, got {lot1_statistic['notes']}"
    assert (
        lot1_statistic["scope"] == "complaints"
    ), f"Expected scope 'complaints' for LOT-0001, got {lot1_statistic['scope']}"

    lot2_statistic = next(
        (stat for stat in result["statistics"] if stat["relatedLot"] == "LOT-0002"),
        None,
    )
    assert lot2_statistic is not None, "Expected statistic for LOT-0002"
    assert (
        lot2_statistic["measure"] == "ab-low"
    ), f"Expected measure 'ab-low' for LOT-0002, got {lot2_statistic['measure']}"
    assert (
        lot2_statistic["notes"] == "Unjustified rejection of abnormally low tenders"
    ), f"Expected notes 'Unjustified rejection of abnormally low tenders' for LOT-0002, got {lot2_statistic['notes']}"
    assert (
        lot2_statistic["scope"] == "complaints"
    ), f"Expected scope 'complaints' for LOT-0002, got {lot2_statistic['scope']}"

    # logger.info("Test bt_660_lotresult_integration passed successfully.") # Logging disabled


if __name__ == "__main__":
    pytest.main(["-v", "-s"])
