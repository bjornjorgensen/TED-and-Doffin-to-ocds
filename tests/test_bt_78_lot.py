# tests/test_bt_78_Lot.py
import json
import logging
import sys
import tempfile
from pathlib import Path

import pytest

from src.ted_and_doffin_to_ocds.converters.eforms.bt_78_lot import (
    merge_security_clearance_deadline,
    parse_security_clearance_deadline,
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


def test_parse_security_clearance_deadline() -> None:
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
        xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
        xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:TenderingTerms>
                <cbc:LatestSecurityClearanceDate>2019-11-15+01:00</cbc:LatestSecurityClearanceDate>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </ContractAwardNotice>
    """

    result = parse_security_clearance_deadline(xml_content)

    assert result is not None
    assert "tender" in result
    assert "lots" in result["tender"]
    assert len(result["tender"]["lots"]) == 1
    assert result["tender"]["lots"][0]["id"] == "LOT-0001"
    assert "milestones" in result["tender"]["lots"][0]
    assert len(result["tender"]["lots"][0]["milestones"]) == 1
    assert result["tender"]["lots"][0]["milestones"][0]["id"] == "1"
    assert (
        result["tender"]["lots"][0]["milestones"][0]["type"]
        == "securityClearanceDeadline"
    )
    assert (
        result["tender"]["lots"][0]["milestones"][0]["dueDate"]
        == "2019-11-15T23:59:59+01:00"
    )


def test_merge_security_clearance_deadline() -> None:
    release_json = {"tender": {"lots": [{"id": "LOT-0001", "title": "Existing Lot"}]}}

    security_clearance_data = {
        "tender": {
            "lots": [
                {
                    "id": "LOT-0001",
                    "milestones": [
                        {
                            "id": "1",
                            "type": "securityClearanceDeadline",
                            "dueDate": "2019-11-15T23:59:59+01:00",
                        },
                    ],
                },
            ],
        },
    }

    merge_security_clearance_deadline(release_json, security_clearance_data)

    assert "milestones" in release_json["tender"]["lots"][0]
    assert len(release_json["tender"]["lots"][0]["milestones"]) == 1
    assert (
        release_json["tender"]["lots"][0]["milestones"][0]["type"]
        == "securityClearanceDeadline"
    )
    assert (
        release_json["tender"]["lots"][0]["milestones"][0]["dueDate"]
        == "2019-11-15T23:59:59+01:00"
    )


def test_bt_78_lot_security_clearance_deadline_integration(
    tmp_path, setup_logging, temp_output_dir
) -> None:
    logger = setup_logging

    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
        xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
        xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cbc:ID>notice-1</cbc:ID>
        <cbc:ContractFolderID>cf-1</cbc:ContractFolderID>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:TenderingTerms>
                <cbc:LatestSecurityClearanceDate>2019-11-15+01:00</cbc:LatestSecurityClearanceDate>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0002</cbc:ID>
            <cac:TenderingTerms>
                <cbc:LatestSecurityClearanceDate>2019-12-01Z</cbc:LatestSecurityClearanceDate>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0003</cbc:ID>
            <cac:TenderingTerms>
                <cbc:OtherTerms>No security clearance needed</cbc:OtherTerms>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </ContractAwardNotice>
    """

    # Create input XML file
    xml_file = tmp_path / "test_input_security_clearance_deadline.xml"
    xml_file.write_text(xml_content)

    # Run main and get result
    result = run_main_and_get_result(xml_file, temp_output_dir)
    logger.info("Result: %s", json.dumps(result, indent=2))

    # Verify the results
    assert "tender" in result
    assert "lots" in result["tender"]

    lots_with_milestones = [
        lot for lot in result["tender"]["lots"] if "milestones" in lot
    ]

    assert len(lots_with_milestones) == 2

    lot_1 = next((lot for lot in lots_with_milestones if lot["id"] == "LOT-0001"), None)
    assert lot_1 is not None
    assert lot_1["milestones"][0]["type"] == "securityClearanceDeadline"
    assert lot_1["milestones"][0]["dueDate"] == "2019-11-15T23:59:59+01:00"

    lot_2 = next((lot for lot in lots_with_milestones if lot["id"] == "LOT-0002"), None)
    assert lot_2 is not None
    assert lot_2["milestones"][0]["type"] == "securityClearanceDeadline"
    assert lot_2["milestones"][0]["dueDate"] == "2019-12-01T23:59:59Z"

    lot_3 = next(
        (lot for lot in result["tender"]["lots"] if lot["id"] == "LOT-0003"), None
    )
    assert lot_3 is not None
    assert "milestones" not in lot_3


if __name__ == "__main__":
    pytest.main(["-v", "-s"])
