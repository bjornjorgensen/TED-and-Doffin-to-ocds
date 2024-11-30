# tests/test_bt_98_Lot.py
import json
import logging
import sys
import tempfile
from pathlib import Path

import pytest

from ted_and_doffin_to_ocds.converters.bt_98_lot import (
    merge_tender_validity_deadline,
    parse_tender_validity_deadline,
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
    output_files = list(output_dir.glob("*.json"))
    assert len(output_files) == 1, f"Expected 1 output file, got {len(output_files)}"
    with output_files[0].open() as f:
        return json.load(f)


def test_parse_tender_validity_deadline() -> None:
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
        xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
        xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:TenderingTerms>
                <cac:TenderValidityPeriod>
                    <cbc:DurationMeasure unitCode="MONTH">4</cbc:DurationMeasure>
                </cac:TenderValidityPeriod>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </ContractAwardNotice>
    """

    result = parse_tender_validity_deadline(xml_content)

    assert result is not None
    assert "tender" in result
    assert "lots" in result["tender"]
    assert len(result["tender"]["lots"]) == 1
    assert result["tender"]["lots"][0]["id"] == "LOT-0001"
    assert (
        result["tender"]["lots"][0]["submissionTerms"]["bidValidityPeriod"][
            "durationInDays"
        ]
        == 120
    )


def test_merge_tender_validity_deadline() -> None:
    release_json = {"tender": {"lots": [{"id": "LOT-0001", "title": "Existing Lot"}]}}

    tender_validity_deadline_data = {
        "tender": {
            "lots": [
                {
                    "id": "LOT-0001",
                    "submissionTerms": {"bidValidityPeriod": {"durationInDays": 120}},
                },
            ],
        },
    }

    merge_tender_validity_deadline(release_json, tender_validity_deadline_data)

    assert "submissionTerms" in release_json["tender"]["lots"][0]
    assert "bidValidityPeriod" in release_json["tender"]["lots"][0]["submissionTerms"]
    assert (
        release_json["tender"]["lots"][0]["submissionTerms"]["bidValidityPeriod"][
            "durationInDays"
        ]
        == 120
    )


def test_bt_98_lot_tender_validity_deadline_integration(
    tmp_path, setup_logging, temp_output_dir
) -> None:
    logger = setup_logging

    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
        xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
        xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:TenderingTerms>
                <cac:TenderValidityPeriod>
                    <cbc:DurationMeasure unitCode="MONTH">4</cbc:DurationMeasure>
                </cac:TenderValidityPeriod>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0002</cbc:ID>
            <cac:TenderingTerms>
                <cac:TenderValidityPeriod>
                    <cbc:DurationMeasure unitCode="WEEK">6</cbc:DurationMeasure>
                </cac:TenderValidityPeriod>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </ContractAwardNotice>
    """

    # Create input XML file
    xml_file = tmp_path / "test_input_tender_validity_deadline.xml"
    xml_file.write_text(xml_content)

    # Run main and get result
    result = run_main_and_get_result(xml_file, temp_output_dir)
    logger.info("Result: %s", json.dumps(result, indent=2))

    # Verify the results
    assert "tender" in result
    assert "lots" in result["tender"]
    assert len(result["tender"]["lots"]) == 2

    lot_1 = next(
        (lot for lot in result["tender"]["lots"] if lot["id"] == "LOT-0001"), None
    )
    assert lot_1 is not None
    assert lot_1["submissionTerms"]["bidValidityPeriod"]["durationInDays"] == 120

    lot_2 = next(
        (lot for lot in result["tender"]["lots"] if lot["id"] == "LOT-0002"), None
    )
    assert lot_2 is not None
    assert lot_2["submissionTerms"]["bidValidityPeriod"]["durationInDays"] == 42


if __name__ == "__main__":
    pytest.main(["-v", "-s"])
