# tests/test_BT_195_160_Tender.py

import pytest
import json
import os
import sys


# Add the parent directory to sys.path to import main and the converter
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ted_and_doffin_to_ocds.main import main
from ted_and_doffin_to_ocds.converters.BT_195_160_Tender import (
    bt_195_bt_160_parse_unpublished_identifier,
    bt_195_bt_160_merge_unpublished_identifier,
)


def create_xml_file(tmp_path, content):
    xml_file = tmp_path / "test_input_unpublished_identifier.xml"
    xml_file.write_text(content)
    return str(xml_file)


def test_bt_195_bt_160_parse_unpublished_identifier():
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
                    </efac:FieldsPrivacy>
                </efac:ConcessionRevenue>
            </efac:LotTender>
        </efac:NoticeResult>
    </root>
    """

    result = bt_195_bt_160_parse_unpublished_identifier(xml_content)

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
        withheld_item["field"] == "con-rev-buy"
    ), "Unexpected withheld information field"
    assert (
        withheld_item["name"] == "Concession Revenue Buyer"
    ), "Unexpected withheld information name"


def test_bt_195_bt_160_merge_unpublished_identifier():
    release_json = {}
    unpublished_identifier_data = {
        "withheldInformation": [
            {
                "id": "con-rev-buy-TEN-0001",
                "field": "con-rev-buy",
                "name": "Concession Revenue Buyer",
            }
        ]
    }

    bt_195_bt_160_merge_unpublished_identifier(
        release_json, unpublished_identifier_data
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


def test_bt_195_bt_160_integration(tmp_path, setup_logging):
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
        withheld_item["field"] == "con-rev-buy"
    ), "Unexpected withheld information field"
    assert (
        withheld_item["name"] == "Concession Revenue Buyer"
    ), "Unexpected withheld information name"


def test_bt_195_bt_160_multiple_items(tmp_path, setup_logging):
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
                    </efac:FieldsPrivacy>
                </efac:ConcessionRevenue>
            </efac:LotTender>
            <efac:LotTender>
                <cbc:ID schemeName="result">TEN-0002</cbc:ID>
                <efac:ConcessionRevenue>
                    <efac:FieldsPrivacy>
                        <efbc:FieldIdentifierCode listName="non-publication-identifier">con-rev-buy</efbc:FieldIdentifierCode>
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
        len(result["withheldInformation"]) == 2
    ), "Expected two withheld information items"

    for i, withheld_item in enumerate(result["withheldInformation"], 1):
        assert (
            withheld_item["id"] == f"con-rev-buy-TEN-000{i}"
        ), f"Unexpected withheld information id for item {i}"
        assert (
            withheld_item["field"] == "con-rev-buy"
        ), f"Unexpected withheld information field for item {i}"
        assert (
            withheld_item["name"] == "Concession Revenue Buyer"
        ), f"Unexpected withheld information name for item {i}"


def test_bt_195_bt_160_no_unpublished_identifier(tmp_path, setup_logging):
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
                    <!-- No FieldsPrivacy element -->
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

    assert (
        "withheldInformation" not in result
    ), "Expected no 'withheldInformation' in result"


if __name__ == "__main__":
    pytest.main(["-v", "-s"])
