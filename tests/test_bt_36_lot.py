# tests/test_bt_36_lot.py
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
    main(str(xml_file), str(output_dir), "ocds-test-prefix", "test-scheme")
    output_files = list(output_dir.glob("*_release_0.json"))
    assert len(output_files) == 1, f"Expected 1 output file, got {len(output_files)}"
    with output_files[0].open() as f:
        return json.load(f)


def test_bt_36_lot_integration(tmp_path, setup_logging, temp_output_dir):
    logger = setup_logging

    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
        xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
        xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cbc:ID>notice-1</cbc:ID>
        <cbc:ContractFolderID>cf-1</cbc:ContractFolderID>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:ProcurementProject>
                <cac:PlannedPeriod>
                    <cbc:DurationMeasure unitCode="DAY">3</cbc:DurationMeasure>
                </cac:PlannedPeriod>
            </cac:ProcurementProject>
        </cac:ProcurementProjectLot>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0002</cbc:ID>
            <cac:ProcurementProject>
                <cac:PlannedPeriod>
                    <cbc:DurationMeasure unitCode="MONTH">2</cbc:DurationMeasure>
                </cac:PlannedPeriod>
            </cac:ProcurementProject>
        </cac:ProcurementProjectLot>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0003</cbc:ID>
            <cac:ProcurementProject>
                <cac:PlannedPeriod>
                    <cbc:DurationMeasure unitCode="YEAR">1</cbc:DurationMeasure>
                </cac:PlannedPeriod>
            </cac:ProcurementProject>
        </cac:ProcurementProjectLot>
    </ContractAwardNotice>
    """
    xml_file = tmp_path / "test_input_lot_duration.xml"
    xml_file.write_text(xml_content)

    # Run main and get result
    result = run_main_and_get_result(xml_file, temp_output_dir)

    logger.info("Test result: %s", json.dumps(result, indent=2))

    # Verify the results
    assert "tender" in result, "Expected 'tender' in result"
    assert "lots" in result["tender"], "Expected 'lots' in tender"
    assert (
        len(result["tender"]["lots"]) == 3
    ), f"Expected 3 lots, got {len(result['tender']['lots'])}"

    lot1 = next(lot for lot in result["tender"]["lots"] if lot["id"] == "LOT-0001")
    assert (
        lot1["contractPeriod"]["durationInDays"] == 3
    ), f"Expected duration 3 days for LOT-0001, got {lot1['contractPeriod']['durationInDays']}"

    lot2 = next(lot for lot in result["tender"]["lots"] if lot["id"] == "LOT-0002")
    assert (
        lot2["contractPeriod"]["durationInDays"] == 60
    ), f"Expected duration 60 days for LOT-0002, got {lot2['contractPeriod']['durationInDays']}"

    lot3 = next(lot for lot in result["tender"]["lots"] if lot["id"] == "LOT-0003")
    assert (
        lot3["contractPeriod"]["durationInDays"] == 365
    ), f"Expected duration 365 days for LOT-0003, got {lot3['contractPeriod']['durationInDays']}"


if __name__ == "__main__":
    pytest.main(["-v"])
