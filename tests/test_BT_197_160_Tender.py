# tests/test_BT_197_160_Tender.py

import pytest
import json
import os
import sys
import logging

# Add the parent directory to sys.path to import main and the converter
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.ted_and_doffin_to_ocds.main import main, configure_logging
from src.ted_and_doffin_to_ocds.converters.BT_197_160_Tender import (
    bt_197_bt_160_parse_unpublished_justification_code,
    bt_197_bt_160_merge_unpublished_justification_code,
)


@pytest.fixture(scope="module")
def setup_logging():
    configure_logging()
    return logging.getLogger(__name__)


def create_xml_file(tmp_path, content):
    xml_file = tmp_path / "test_input_unpublished_justification_code.xml"
    xml_file.write_text(content)
    return str(xml_file)


def test_bt_197_bt_160_parse_unpublished_justification_code(setup_logging):
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
                        <cbc:ReasonCode listName="non-publication-justification">oth-int</cbc:ReasonCode>
                    </efac:FieldsPrivacy>
                </efac:ConcessionRevenue>
            </efac:LotTender>
        </efac:NoticeResult>
    </root>
    """

    result = bt_197_bt_160_parse_unpublished_justification_code(xml_content)

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
        "rationaleClassifications" in withheld_item
    ), "Expected 'rationaleClassifications' in withheld item"
    assert (
        len(withheld_item["rationaleClassifications"]) == 1
    ), "Expected one rationale classification"

    classification = withheld_item["rationaleClassifications"][0]
    assert (
        classification["scheme"] == "non-publication-justification"
    ), "Unexpected scheme"
    assert classification["id"] == "oth-int", "Unexpected id"
    assert (
        classification["description"] == "Other public interest"
    ), "Unexpected description"
    assert (
        classification["uri"]
        == "http://publications.europa.eu/resource/authority/non-publication-justification/oth-int"
    ), "Unexpected URI"


def test_bt_197_bt_160_merge_unpublished_justification_code(setup_logging):
    release_json = {
        "withheldInformation": [
            {
                "id": "con-rev-buy-TEN-0001",
                "field": "con-rev-buy",
                "name": "Concession Revenue Buyer",
            }
        ]
    }
    unpublished_justification_code_data = {
        "withheldInformation": [
            {
                "id": "con-rev-buy-TEN-0001",
                "rationaleClassifications": [
                    {
                        "scheme": "non-publication-justification",
                        "id": "oth-int",
                        "description": "Other public interest",
                        "uri": "http://publications.europa.eu/resource/authority/non-publication-justification/oth-int",
                    }
                ],
            }
        ]
    }

    bt_197_bt_160_merge_unpublished_justification_code(
        release_json, unpublished_justification_code_data
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
        "rationaleClassifications" in withheld_item
    ), "Expected 'rationaleClassifications' in withheld item"
    assert (
        len(withheld_item["rationaleClassifications"]) == 1
    ), "Expected one rationale classification"

    classification = withheld_item["rationaleClassifications"][0]
    assert (
        classification["scheme"] == "non-publication-justification"
    ), "Unexpected scheme"
    assert classification["id"] == "oth-int", "Unexpected id"
    assert (
        classification["description"] == "Other public interest"
    ), "Unexpected description"
    assert (
        classification["uri"]
        == "http://publications.europa.eu/resource/authority/non-publication-justification/oth-int"
    ), "Unexpected URI"


def test_bt_197_bt_160_integration(tmp_path, setup_logging):
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
                        <cbc:ReasonCode listName="non-publication-justification">oth-int</cbc:ReasonCode>
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
        "rationaleClassifications" in withheld_item
    ), "Expected 'rationaleClassifications' in withheld item"
    assert (
        len(withheld_item["rationaleClassifications"]) == 1
    ), "Expected one rationale classification"

    classification = withheld_item["rationaleClassifications"][0]
    assert (
        classification["scheme"] == "non-publication-justification"
    ), "Unexpected scheme"
    assert classification["id"] == "oth-int", "Unexpected id"
    assert (
        classification["description"] == "Other public interest"
    ), "Unexpected description"
    assert (
        classification["uri"]
        == "http://publications.europa.eu/resource/authority/non-publication-justification/oth-int"
    ), "Unexpected URI"


def test_bt_197_bt_160_unknown_code(setup_logging):
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
                        <cbc:ReasonCode listName="non-publication-justification">unknown-code</cbc:ReasonCode>
                    </efac:FieldsPrivacy>
                </efac:ConcessionRevenue>
            </efac:LotTender>
        </efac:NoticeResult>
    </root>
    """

    result = bt_197_bt_160_parse_unpublished_justification_code(xml_content)

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
        "rationaleClassifications" in withheld_item
    ), "Expected 'rationaleClassifications' in withheld item"
    assert (
        len(withheld_item["rationaleClassifications"]) == 1
    ), "Expected one rationale classification"

    classification = withheld_item["rationaleClassifications"][0]
    assert (
        classification["scheme"] == "non-publication-justification"
    ), "Unexpected scheme"
    assert classification["id"] == "unknown-code", "Unexpected id"
    assert (
        "description" not in classification
    ), "Unexpected description for unknown code"
    assert "uri" not in classification, "Unexpected URI for unknown code"


def test_bt_197_bt_160_multiple_items(tmp_path, setup_logging):
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
                        <cbc:ReasonCode listName="non-publication-justification">oth-int</cbc:ReasonCode>
                    </efac:FieldsPrivacy>
                </efac:ConcessionRevenue>
            </efac:LotTender>
            <efac:LotTender>
                <cbc:ID schemeName="result">TEN-0002</cbc:ID>
                <efac:ConcessionRevenue>
                    <efac:FieldsPrivacy>
                        <efbc:FieldIdentifierCode listName="non-publication-identifier">con-rev-buy</efbc:FieldIdentifierCode>
                        <cbc:ReasonCode listName="non-publication-justification">fair-comp</cbc:ReasonCode>
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
            "rationaleClassifications" in withheld_item
        ), f"Expected 'rationaleClassifications' in withheld item {i}"
        assert (
            len(withheld_item["rationaleClassifications"]) == 1
        ), f"Expected one rationale classification for item {i}"

        classification = withheld_item["rationaleClassifications"][0]
        assert (
            classification["scheme"] == "non-publication-justification"
        ), f"Unexpected scheme for item {i}"

        if i == 1:
            assert classification["id"] == "oth-int", "Unexpected id for item 1"
            assert (
                classification["description"] == "Other public interest"
            ), "Unexpected description for item 1"
            assert (
                classification["uri"]
                == "http://publications.europa.eu/resource/authority/non-publication-justification/oth-int"
            ), "Unexpected URI for item 1"
        elif i == 2:
            assert classification["id"] == "fair-comp", "Unexpected id for item 2"
            assert (
                classification["description"] == "Fair competition"
            ), "Unexpected description for item 2"
            assert (
                classification["uri"]
                == "http://publications.europa.eu/resource/authority/non-publication-justification/fair-comp"
            ), "Unexpected URI for item 2"


if __name__ == "__main__":
    pytest.main(["-v", "-s"])