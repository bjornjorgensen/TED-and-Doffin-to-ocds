from pathlib import Path
import pytest
from ted_and_doffin_to_ocds.converters.bt_767_lot import (
    parse_electronic_auction,
    merge_electronic_auction,
)
import json
import sys
import tempfile
import logging

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
    output_files = list(output_dir.glob("*.json"))
    assert len(output_files) == 1, f"Expected 1 output file, got {len(output_files)}"
    with output_files[0].open() as f:
        return json.load(f)


def test_parse_electronic_auction():
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
    assert "tender" in result
    assert "lots" in result["tender"]
    assert len(result["tender"]["lots"]) == 1
    assert result["tender"]["lots"][0]["id"] == "LOT-0001"
    assert result["tender"]["lots"][0]["techniques"]["hasElectronicAuction"] is True


def test_merge_electronic_auction():
    release_json = {"tender": {"lots": [{"id": "LOT-0001", "title": "Existing Lot"}]}}

    electronic_auction_data = {
        "tender": {
            "lots": [{"id": "LOT-0001", "techniques": {"hasElectronicAuction": True}}],
        },
    }

    merge_electronic_auction(release_json, electronic_auction_data)

    assert "techniques" in release_json["tender"]["lots"][0]
    assert (
        release_json["tender"]["lots"][0]["techniques"]["hasElectronicAuction"] is True
    )


def test_bt_767_lot_electronic_auction_integration(tmp_path, temp_output_dir):
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

    result = run_main_and_get_result(xml_file, temp_output_dir)

    with Path(temp_output_dir / "output.json").open() as f:
        result = json.load(f)

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
