# tests/test_bt_5101_Lot.py
from pathlib import Path
import pytest
import json
import sys
import logging

# Add the parent directory to sys.path to import main
sys.path.append(str(Path(__file__).parent.parent))
from src.ted_and_doffin_to_ocds.main import main, configure_logging
from ted_and_doffin_to_ocds.converters.bt_5101_lot import (
    parse_place_performance_street_lot,
    merge_place_performance_street_lot,
)


@pytest.fixture(scope="module")
def setup_logging():
    configure_logging()
    return logging.getLogger(__name__)


def test_parse_place_performance_street_lot():
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:ProcurementProject>
                <cac:RealizedLocation>
                    <cac:Address>
                        <cbc:StreetName>Main Street</cbc:StreetName>
                        <cbc:AdditionalStreetName>Building B1</cbc:AdditionalStreetName>
                        <cac:AddressLine>
                            <cbc:Line>3rd floor</cbc:Line>
                        </cac:AddressLine>
                        <cac:AddressLine>
                            <cbc:Line>Suite 300</cbc:Line>
                        </cac:AddressLine>
                    </cac:Address>
                </cac:RealizedLocation>
            </cac:ProcurementProject>
        </cac:ProcurementProjectLot>
    </root>
    """

    result = parse_place_performance_street_lot(xml_content)

    assert result is not None
    assert "tender" in result
    assert "items" in result["tender"]
    assert len(result["tender"]["items"]) == 1
    assert result["tender"]["items"][0]["relatedLot"] == "LOT-0001"
    assert (
        result["tender"]["items"][0]["deliveryAddresses"][0]["streetAddress"]
        == "Main Street, Building B1, 3rd floor, Suite 300"
    )


def test_merge_place_performance_street_lot():
    release_json = {
        "tender": {
            "items": [
                {
                    "id": "1",
                    "relatedLot": "LOT-0001",
                    "deliveryAddresses": [{"region": "UKG23"}],
                },
            ],
        },
    }

    street_data = {
        "tender": {
            "items": [
                {
                    "id": "1",
                    "relatedLot": "LOT-0001",
                    "deliveryAddresses": [
                        {
                            "streetAddress": "Main Street, Building B1, 3rd floor, Suite 300",
                        },
                    ],
                },
            ],
        },
    }

    merge_place_performance_street_lot(release_json, street_data)

    assert len(release_json["tender"]["items"]) == 1
    assert release_json["tender"]["items"][0]["relatedLot"] == "LOT-0001"
    assert len(release_json["tender"]["items"][0]["deliveryAddresses"]) == 1
    assert (
        release_json["tender"]["items"][0]["deliveryAddresses"][0]["region"] == "UKG23"
    )
    assert (
        release_json["tender"]["items"][0]["deliveryAddresses"][0]["streetAddress"]
        == "Main Street, Building B1, 3rd floor, Suite 300"
    )


def test_bt_5101_lot_integration(tmp_path, setup_logging):
    logger = setup_logging
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:ProcurementProject>
                <cac:RealizedLocation>
                    <cac:Address>
                        <cbc:StreetName>Main Street</cbc:StreetName>
                        <cbc:AdditionalStreetName>Building B1</cbc:AdditionalStreetName>
                        <cac:AddressLine>
                            <cbc:Line>3rd floor</cbc:Line>
                        </cac:AddressLine>
                        <cac:AddressLine>
                            <cbc:Line>Suite 300</cbc:Line>
                        </cac:AddressLine>
                    </cac:Address>
                </cac:RealizedLocation>
            </cac:ProcurementProject>
        </cac:ProcurementProjectLot>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0002</cbc:ID>
            <cac:ProcurementProject>
                <cac:RealizedLocation>
                    <cac:Address>
                        <cbc:StreetName>Second Avenue</cbc:StreetName>
                        <cbc:AdditionalStreetName>Suite 100</cbc:AdditionalStreetName>
                        <cac:AddressLine>
                            <cbc:Line>Floor 5</cbc:Line>
                        </cac:AddressLine>
                    </cac:Address>
                </cac:RealizedLocation>
            </cac:ProcurementProject>
        </cac:ProcurementProjectLot>
    </root>
    """
    xml_file = tmp_path / "test_input_bt_5101_lot.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with Path("output.json").open() as f:
        result = json.load(f)

    logger.info("Result: %s", json.dumps(result, indent=2))

    assert "tender" in result
    assert "items" in result["tender"]
    assert len(result["tender"]["items"]) == 2

    lot_1_item = next(
        item for item in result["tender"]["items"] if item["relatedLot"] == "LOT-0001"
    )
    assert (
        lot_1_item["deliveryAddresses"][0]["streetAddress"]
        == "Main Street, Building B1, 3rd floor, Suite 300"
    )

    lot_2_item = next(
        item for item in result["tender"]["items"] if item["relatedLot"] == "LOT-0002"
    )
    assert (
        lot_2_item["deliveryAddresses"][0]["streetAddress"]
        == "Second Avenue, Suite 100, Floor 5"
    )


def test_bt_5101_lot_missing_data(tmp_path, setup_logging):
    logger = setup_logging
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:ProcurementProject>
                <cac:RealizedLocation>
                    <cac:Address>
                        <!-- Missing all address elements -->
                    </cac:Address>
                </cac:RealizedLocation>
            </cac:ProcurementProject>
        </cac:ProcurementProjectLot>
    </root>
    """
    xml_file = tmp_path / "test_input_bt_5101_lot_missing.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with Path("output.json").open() as f:
        result = json.load(f)

    logger.info("Result: %s", json.dumps(result, indent=2))

    assert "tender" in result
    assert "items" not in result["tender"] or len(result["tender"]["items"]) == 0


if __name__ == "__main__":
    pytest.main()
