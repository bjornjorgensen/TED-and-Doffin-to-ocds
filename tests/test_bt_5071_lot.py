# tests/test_bt_5071_Lot.py
from pathlib import Path
import pytest
import json
import sys
import logging

# Add the parent directory to sys.path to import main
sys.path.append(str(Path(__file__).parent.parent))
from src.ted_and_doffin_to_ocds.main import main, configure_logging
from ted_and_doffin_to_ocds.converters.bt_5071_lot import (
    parse_place_performance_country_subdivision,
    merge_place_performance_country_subdivision,
)


@pytest.fixture(scope="module")
def setup_logging():
    configure_logging()
    return logging.getLogger(__name__)


def test_parse_place_performance_country_subdivision():
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:ProcurementProject>
                <cac:RealizedLocation>
                    <cac:Address>
                        <cbc:CountrySubentityCode listName="nuts=lvl3">UKG23</cbc:CountrySubentityCode>
                    </cac:Address>
                </cac:RealizedLocation>
            </cac:ProcurementProject>
        </cac:ProcurementProjectLot>
    </root>
    """

    result = parse_place_performance_country_subdivision(xml_content)

    assert result is not None
    assert "tender" in result
    assert "items" in result["tender"]
    assert len(result["tender"]["items"]) == 1
    assert result["tender"]["items"][0]["relatedLot"] == "LOT-0001"
    assert result["tender"]["items"][0]["deliveryAddresses"][0]["region"] == "UKG23"


def test_merge_place_performance_country_subdivision():
    release_json = {
        "tender": {
            "items": [
                {
                    "id": "1",
                    "relatedLot": "LOT-0001",
                    "deliveryAddresses": [{"streetAddress": "123 Main St"}],
                },
            ],
        },
    }

    subdivision_data = {
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

    merge_place_performance_country_subdivision(release_json, subdivision_data)

    assert len(release_json["tender"]["items"]) == 1
    assert release_json["tender"]["items"][0]["relatedLot"] == "LOT-0001"
    assert len(release_json["tender"]["items"][0]["deliveryAddresses"]) == 1
    assert (
        release_json["tender"]["items"][0]["deliveryAddresses"][0]["streetAddress"]
        == "123 Main St"
    )
    assert (
        release_json["tender"]["items"][0]["deliveryAddresses"][0]["region"] == "UKG23"
    )


def test_bt_5071_lot_integration(tmp_path, setup_logging):
    logger = setup_logging
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:ProcurementProject>
                <cac:RealizedLocation>
                    <cac:Address>
                        <cbc:CountrySubentityCode listName="nuts=lvl3">UKG23</cbc:CountrySubentityCode>
                    </cac:Address>
                </cac:RealizedLocation>
            </cac:ProcurementProject>
        </cac:ProcurementProjectLot>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0002</cbc:ID>
            <cac:ProcurementProject>
                <cac:RealizedLocation>
                    <cac:Address>
                        <cbc:CountrySubentityCode listName="nuts=lvl3">UKG24</cbc:CountrySubentityCode>
                    </cac:Address>
                </cac:RealizedLocation>
                <cac:RealizedLocation>
                    <cac:Address>
                        <cbc:CountrySubentityCode listName="nuts=lvl3">UKG25</cbc:CountrySubentityCode>
                    </cac:Address>
                </cac:RealizedLocation>
            </cac:ProcurementProject>
        </cac:ProcurementProjectLot>
    </root>
    """
    xml_file = tmp_path / "test_input_bt_5071.xml"
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
    assert len(lot_1_item["deliveryAddresses"]) == 1
    assert lot_1_item["deliveryAddresses"][0]["region"] == "UKG23"

    lot_2_item = next(
        item for item in result["tender"]["items"] if item["relatedLot"] == "LOT-0002"
    )
    assert len(lot_2_item["deliveryAddresses"]) == 2
    assert {addr["region"] for addr in lot_2_item["deliveryAddresses"]} == {
        "UKG24",
        "UKG25",
    }


def test_bt_5071_lot_missing_data(tmp_path, setup_logging):
    logger = setup_logging
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:ProcurementProject>
                <cac:RealizedLocation>
                    <cac:Address>
                        <!-- Missing CountrySubentityCode -->
                    </cac:Address>
                </cac:RealizedLocation>
            </cac:ProcurementProject>
        </cac:ProcurementProjectLot>
    </root>
    """
    xml_file = tmp_path / "test_input_bt_5071_missing.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with Path("output.json").open() as f:
        result = json.load(f)

    logger.info("Result: %s", json.dumps(result, indent=2))

    assert "tender" in result
    assert "items" not in result["tender"] or len(result["tender"]["items"]) == 0


if __name__ == "__main__":
    pytest.main()
