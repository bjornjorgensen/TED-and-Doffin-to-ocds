# tests/test_bt_27_lot.py
import json
import logging
import sys
import tempfile
from pathlib import Path

import pytest

from src.ted_and_doffin_to_ocds.converters.eforms.bt_27_lot import (
    merge_lot_estimated_value,
    parse_lot_estimated_value,
)

# Add the parent directory to sys.path to import main
sys.path.append(str(Path(__file__).parent.parent))
from src.ted_and_doffin_to_ocds.main import configure_logging, main


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


def test_parse_lot_estimated_value() -> None:
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:ProcurementProject>
                <cac:RequestedTenderTotal>
                    <cbc:EstimatedOverallContractAmount currencyID="EUR">250000</cbc:EstimatedOverallContractAmount>
                </cac:RequestedTenderTotal>
            </cac:ProcurementProject>
        </cac:ProcurementProjectLot>
    </root>
    """

    result = parse_lot_estimated_value(xml_content)

    assert result is not None
    assert "tender" in result
    assert "lots" in result["tender"]
    assert len(result["tender"]["lots"]) == 1
    assert result["tender"]["lots"][0]["id"] == "LOT-0001"
    assert result["tender"]["lots"][0]["value"]["amount"] == 250000
    assert result["tender"]["lots"][0]["value"]["currency"] == "EUR"


def test_merge_lot_estimated_value() -> None:
    release_json = {"tender": {"lots": [{"id": "LOT-0001", "title": "Existing Lot"}]}}

    lot_estimated_value_data = {
        "tender": {
            "lots": [
                {"id": "LOT-0001", "value": {"amount": 250000, "currency": "EUR"}},
            ],
        },
    }

    merge_lot_estimated_value(release_json, lot_estimated_value_data)

    assert "value" in release_json["tender"]["lots"][0]
    assert release_json["tender"]["lots"][0]["value"]["amount"] == 250000
    assert release_json["tender"]["lots"][0]["value"]["currency"] == "EUR"


def test_bt_27_lot_integration(tmp_path, setup_logging, temp_output_dir) -> None:
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
                <cac:RequestedTenderTotal>
                    <cbc:EstimatedOverallContractAmount currencyID="EUR">250000</cbc:EstimatedOverallContractAmount>
                </cac:RequestedTenderTotal>
            </cac:ProcurementProject>
        </cac:ProcurementProjectLot>
    </ContractAwardNotice>
    """
    xml_file = tmp_path / "test_input_lot_estimated_value.xml"
    xml_file.write_text(xml_content)

    # Run main and get result
    result = run_main_and_get_result(xml_file, temp_output_dir)

    logger.info("Result: %s", json.dumps(result, indent=2))

    assert "tender" in result
    assert "lots" in result["tender"]
    assert len(result["tender"]["lots"]) == 1
    assert result["tender"]["lots"][0]["id"] == "LOT-0001"
    assert result["tender"]["lots"][0]["value"]["amount"] == 250000
    assert result["tender"]["lots"][0]["value"]["currency"] == "EUR"


if __name__ == "__main__":
    pytest.main(["-v", "-s"])
