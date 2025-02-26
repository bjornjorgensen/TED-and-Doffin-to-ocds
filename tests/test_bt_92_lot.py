# tests/test_bt_92_Lot.py
import json
import logging
import sys
import tempfile
from pathlib import Path

import pytest

from src.ted_and_doffin_to_ocds.converters.eforms.bt_92_lot import (
    merge_electronic_ordering,
    parse_electronic_ordering,
)

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


def test_parse_electronic_ordering() -> None:
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
        xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
        xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID>LOT-0001</cbc:ID>
            <cac:TenderingTerms>
                <cac:PostAwardProcess>
                    <cbc:ElectronicOrderUsageIndicator>true</cbc:ElectronicOrderUsageIndicator>
                </cac:PostAwardProcess>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </ContractAwardNotice>
    """

    result = parse_electronic_ordering(xml_content)

    assert result is not None
    assert "tender" in result
    assert "lots" in result["tender"]
    assert len(result["tender"]["lots"]) == 1
    assert result["tender"]["lots"][0]["id"] == "LOT-0001"
    assert result["tender"]["lots"][0]["contractTerms"]["hasElectronicOrdering"] is True


def test_merge_electronic_ordering() -> None:
    release_json = {"tender": {"lots": [{"id": "LOT-0001", "title": "Existing Lot"}]}}

    electronic_ordering_data = {
        "tender": {
            "lots": [
                {"id": "LOT-0001", "contractTerms": {"hasElectronicOrdering": True}},
            ],
        },
    }

    merge_electronic_ordering(release_json, electronic_ordering_data)

    assert "contractTerms" in release_json["tender"]["lots"][0]
    assert (
        release_json["tender"]["lots"][0]["contractTerms"]["hasElectronicOrdering"]
        is True
    )


def test_bt_92_lot_electronic_ordering_integration(
    tmp_path, setup_logging, temp_output_dir
) -> None:
    logger = setup_logging

    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
        xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
        xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID>LOT-0001</cbc:ID>
            <cac:TenderingTerms>
                <cac:PostAwardProcess>
                    <cbc:ElectronicOrderUsageIndicator>true</cbc:ElectronicOrderUsageIndicator>
                </cac:PostAwardProcess>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
        <cac:ProcurementProjectLot>
            <cbc:ID>LOT-0002</cbc:ID>
            <cac:TenderingTerms>
                <cac:PostAwardProcess>
                    <cbc:ElectronicOrderUsageIndicator>false</cbc:ElectronicOrderUsageIndicator>
                </cac:PostAwardProcess>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </ContractAwardNotice>
    """

    # Create input XML file
    xml_file = tmp_path / "test_input_electronic_ordering.xml"
    xml_file.write_text(xml_content)

    # Run main and get result
    result = run_main_and_get_result(xml_file, temp_output_dir)
    # logger.info("Result: %s", json.dumps(result, indent=2) # Logging disabled)

    # Verify the results
    assert "tender" in result
    assert "lots" in result["tender"]
    assert len(result["tender"]["lots"]) == 2

    lot_1 = next(
        (lot for lot in result["tender"]["lots"] if lot["id"] == "LOT-0001"), None
    )
    assert lot_1 is not None
    assert lot_1["contractTerms"]["hasElectronicOrdering"] is True

    lot_2 = next(
        (lot for lot in result["tender"]["lots"] if lot["id"] == "LOT-0002"), None
    )
    assert lot_2 is not None
    assert lot_2["contractTerms"]["hasElectronicOrdering"] is False


if __name__ == "__main__":
    pytest.main(["-v", "-s"])
