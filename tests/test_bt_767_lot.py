import json
import logging
import os
import sys
import tempfile
from pathlib import Path

import pytest

from src.ted_and_doffin_to_ocds.converters.eforms.bt_767_lot import (
    merge_electronic_auction,
    parse_electronic_auction,
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
    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate a unique release ID based on file stem
    release_id = f"ocds-test-{xml_file.stem}"

    logger = logging.getLogger(__name__)
    logger.debug("Running main with release_id %s", release_id)
    logger.debug("Output directory: %s", output_dir)

    main(str(xml_file), str(output_dir), release_id, "test-scheme")

    # List all files in output directory for debugging
    all_files = list(output_dir.glob("*.json"))
    logger.debug("Files in output directory: %s", [f.name for f in all_files])

    # Look for the release file with more flexible pattern
    output_files = list(output_dir.glob("*.json"))
    if not output_files:
        # If no files found, check directory exists and is writable
        # If no files found, check directory exists and is writable
        logger.error("No output files found in %s", output_dir)
        logger.debug("Directory exists: %s", output_dir.exists())
        logger.debug("Directory writable: %s", os.access(str(output_dir), os.W_OK))

    assert len(output_files) > 0, f"No output files found in {output_dir}"
    return json.loads(output_files[0].read_text())


def test_parse_electronic_auction_true() -> None:
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:TenderingProcess>
                <cac:AuctionTerms>
                    <cbc:AuctionConstraintIndicator>true</cbc:AuctionConstraintIndicator>
                </cac:AuctionTerms>
            </cac:TenderingProcess>
        </cac:ProcurementProjectLot>
    </root>
    """
    result = parse_electronic_auction(xml_content)
    assert result is not None
    assert result["tender"]["lots"][0]["techniques"]["hasElectronicAuction"] is True


def test_parse_electronic_auction_false() -> None:
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:TenderingProcess>
                <cac:AuctionTerms>
                    <cbc:AuctionConstraintIndicator>false</cbc:AuctionConstraintIndicator>
                </cac:AuctionTerms>
            </cac:TenderingProcess>
        </cac:ProcurementProjectLot>
    </root>
    """
    result = parse_electronic_auction(xml_content)
    assert result is not None
    assert result["tender"]["lots"][0]["techniques"]["hasElectronicAuction"] is False


def test_parse_electronic_auction_missing() -> None:
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:TenderingProcess>
            </cac:TenderingProcess>
        </cac:ProcurementProjectLot>
    </root>
    """
    result = parse_electronic_auction(xml_content)
    assert result is None


def test_merge_electronic_auction_new_lot() -> None:
    release_json = {"tender": {"lots": []}}
    electronic_auction_data = {
        "tender": {
            "lots": [{"id": "LOT-0001", "techniques": {"hasElectronicAuction": True}}]
        }
    }
    merge_electronic_auction(release_json, electronic_auction_data)
    assert len(release_json["tender"]["lots"]) == 1
    assert (
        release_json["tender"]["lots"][0]["techniques"]["hasElectronicAuction"] is True
    )


def test_merge_electronic_auction_existing_lot() -> None:
    release_json = {
        "tender": {
            "lots": [
                {
                    "id": "LOT-0001",
                    "title": "Existing Lot",
                    "techniques": {"existingTechnique": True},
                }
            ]
        }
    }
    electronic_auction_data = {
        "tender": {
            "lots": [{"id": "LOT-0001", "techniques": {"hasElectronicAuction": True}}]
        }
    }
    merge_electronic_auction(release_json, electronic_auction_data)
    assert release_json["tender"]["lots"][0]["techniques"]["existingTechnique"] is True
    assert (
        release_json["tender"]["lots"][0]["techniques"]["hasElectronicAuction"] is True
    )


def test_merge_electronic_auction_none_data() -> None:
    release_json = {"tender": {"lots": []}}
    merge_electronic_auction(release_json, None)
    assert release_json == {"tender": {"lots": []}}


def test_bt_767_lot_electronic_auction_integration(
    tmp_path, temp_output_dir, setup_logging
) -> None:
    logger = setup_logging
    logger.debug("Starting integration test")

    xml_content = """
    <ContractNotice xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:TenderingProcess>
                <cac:AuctionTerms>
                    <cbc:AuctionConstraintIndicator>true</cbc:AuctionConstraintIndicator>
                </cac:AuctionTerms>
            </cac:TenderingProcess>
        </cac:ProcurementProjectLot>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0002</cbc:ID>
            <cac:TenderingProcess>
                <cac:AuctionTerms>
                    <cbc:AuctionConstraintIndicator>false</cbc:AuctionConstraintIndicator>
                </cac:AuctionTerms>
            </cac:TenderingProcess>
        </cac:ProcurementProjectLot>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0003</cbc:ID>
            <cac:TenderingProcess>
                <cac:OtherTerms>
                    <cbc:SomeOtherIndicator>true</cbc:SomeOtherIndicator>
                </cac:OtherTerms>
            </cac:TenderingProcess>
        </cac:ProcurementProjectLot>
    </ContractNotice>
    """
    xml_file = tmp_path / "test_input_electronic_auction.xml"
    xml_file.write_text(xml_content)
    logger.debug("Created test XML file: %s", xml_file)

    result = run_main_and_get_result(xml_file, temp_output_dir)

    # Remove redundant file read since result is already loaded
    assert "tender" in result
    assert "lots" in result["tender"]

    lots_with_electronic_auction = [
        lot
        for lot in result["tender"]["lots"]
        if "techniques" in lot and "hasElectronicAuction" in lot["techniques"]
    ]
    assert len(lots_with_electronic_auction) == 2

    lot_1 = next(
        (lot for lot in lots_with_electronic_auction if lot["id"] == "LOT-0001"),
        None,
    )
    assert lot_1 is not None
    assert lot_1["techniques"]["hasElectronicAuction"] is True

    lot_2 = next(
        (lot for lot in lots_with_electronic_auction if lot["id"] == "LOT-0002"),
        None,
    )
    assert lot_2 is not None
    assert lot_2["techniques"]["hasElectronicAuction"] is False

    lot_3 = next(
        (lot for lot in result["tender"]["lots"] if lot["id"] == "LOT-0003"),
        None,
    )
    assert lot_3 is not None
    assert "techniques" not in lot_3 or "hasElectronicAuction" not in lot_3.get(
        "techniques",
        {},
    )


if __name__ == "__main__":
    pytest.main(["-v", "-s"])
