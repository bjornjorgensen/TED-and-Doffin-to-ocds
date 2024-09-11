# tests/test_BT_198_160_Tender.py

import pytest
import json
import os
import sys
import logging

# Add the parent directory to sys.path to import main and the converter
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.ted_and_doffin_to_ocds.main import main, configure_logging
from src.ted_and_doffin_to_ocds.converters.BT_198_160_Tender import (
    bt_198_bt_160_parse_unpublished_access_date,
    bt_198_bt_160_merge_unpublished_access_date,
)


@pytest.fixture(scope="module")
def setup_logging():
    configure_logging()
    return logging.getLogger(__name__)


def create_xml_file(tmp_path, content):
    xml_file = tmp_path / "test_input_unpublished_access_date.xml"
    xml_file.write_text(content)
    return str(xml_file)


def test_bt_198_bt_160_parse_unpublished_access_date(setup_logging):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
          xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
          xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1">
        <efac:NoticeResult>
            <efac:LotTender>
                <cbc:ID schemeName="result">TEN-0001</cbc:ID>
                <efac:ConcessionRevenue>
                    <efac:FieldsPrivacy>
                        <efbc:FieldIdentifierCode listName="non-publication-identifier">con-rev-buy</efbc:FieldIdentifierCode>
                        <efbc:PublicationDate>2025-03-31+01:00</efbc:PublicationDate>
                    </efac:FieldsPrivacy>
                </efac:ConcessionRevenue>
            </efac:LotTender>
        </efac:NoticeResult>
    </root>
    """

    result = bt_198_bt_160_parse_unpublished_access_date(xml_content)

    assert result is not None, "Expected parsed data, got None"
    assert "withheldInformation" in result, "Expected 'withheldInformation' in result"
    assert (
        len(result["withheldInformation"]) == 1
    ), "Expected one withheld information item"

    withheld_item = result["withheldInformation"][0]
    assert (
        withheld_item["id"] == "con-rev-buy-TEN-0001"
    ), "Unexpected withheld information id"
    assert (
        withheld_item["availabilityDate"] == "2025-03-31T00:00:00+01:00"
    ), "Unexpected availability date"


def test_bt_198_bt_160_merge_unpublished_access_date(setup_logging):
    release_json = {
        "withheldInformation": [
            {
                "id": "con-rev-buy-TEN-0001",
                "field": "con-rev-buy",
                "name": "Concession Revenue Buyer",
            }
        ]
    }
    unpublished_access_date_data = {
        "withheldInformation": [
            {
                "id": "con-rev-buy-TEN-0001",
                "availabilityDate": "2025-03-31T00:00:00+01:00",
            }
        ]
    }

    bt_198_bt_160_merge_unpublished_access_date(
        release_json, unpublished_access_date_data
    )

    assert (
        "withheldInformation" in release_json
    ), "Expected 'withheldInformation' in release_json"
    assert (
        len(release_json["withheldInformation"]) == 1
    ), "Expected one withheld information item"

    withheld_item = release_json["withheldInformation"][0]
    assert (
        withheld_item["id"] == "con-rev-buy-TEN-0001"
    ), "Unexpected withheld information id"
    assert (
        withheld_item["field"] == "con-rev-buy"
    ), "Unexpected withheld information field"
    assert (
        withheld_item["name"] == "Concession Revenue Buyer"
    ), "Unexpected withheld information name"
    assert (
        withheld_item["availabilityDate"] == "2025-03-31T00:00:00+01:00"
    ), "Unexpected availability date"


def test_btt_198_bt_160_integration(tmp_path, setup_logging):
    logger = setup_logging
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
          xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
          xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1">
        <efac:NoticeResult>
            <efac:LotTender>
                <cbc:ID schemeName="result">TEN-0001</cbc:ID>
                <efac:ConcessionRevenue>
                    <efac:FieldsPrivacy>
                        <efbc:FieldIdentifierCode listName="non-publication-identifier">con-rev-buy</efbc:FieldIdentifierCode>
                        <efbc:PublicationDate>2025-03-31+01:00</efbc:PublicationDate>
                    </efac:FieldsPrivacy>
                </efac:ConcessionRevenue>
            </efac:LotTender>
        </efac:NoticeResult>
    </root>
    """
    xml_file = create_xml_file(tmp_path, xml_content)

    main(xml_file, "ocds-test-prefix")

    with open("output.json") as f:
        result = json.load(f)

    logger.info(f"Result: {json.dumps(result, indent=2)}")

    assert "withheldInformation" in result, "Expected 'withheldInformation' in result"
    assert (
        len(result["withheldInformation"]) == 1
    ), "Expected one withheld information item"

    withheld_item = result["withheldInformation"][0]
    assert (
        withheld_item["id"] == "con-rev-buy-TEN-0001"
    ), "Unexpected withheld information id"
    assert (
        withheld_item["availabilityDate"] == "2025-03-31T00:00:00+01:00"
    ), "Unexpected availability date"


if __name__ == "__main__":
    pytest.main(["-v", "-s"])
