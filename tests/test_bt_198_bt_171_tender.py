# tests/test_bt_198_bt_171_Tender.py

import pytest
import json
import os
import sys
import logging

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.ted_and_doffin_to_ocds.main import main, configure_logging


@pytest.fixture(scope="module")
def setup_logging():
    configure_logging()
    return logging.getLogger(__name__)


def test_bt198_bt171_unpublished_access_date_integration(tmp_path, setup_logging):
    logger = setup_logging
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
          xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
          xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1">
        <efac:noticeResult>
            <efac:LotTender>
                <cbc:ID schemeName="result">TEN-0001</cbc:ID>
                <efac:FieldsPrivacy>
                    <efbc:FieldIdentifierCode>ten-ran</efbc:FieldIdentifierCode>
                    <efbc:PublicationDate>2025-03-31+01:00</efbc:PublicationDate>
                </efac:FieldsPrivacy>
            </efac:LotTender>
        </efac:noticeResult>
    </root>
    """
    xml_file = tmp_path / "test_input_bt198_bt171.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open("output.json") as f:
        result = json.load(f)

    logger.info("Result: %s", json.dumps(result, indent=2))

    assert "withheldInformation" in result, "Expected 'withheldInformation' in result"
    assert (
        len(result["withheldInformation"]) == 1
    ), "Expected one withheld information item"

    withheld_item = result["withheldInformation"][0]
    assert (
        withheld_item["id"] == "ten-ran-TEN-0001"
    ), "Unexpected withheld information id"
    assert withheld_item["field"] == "ten-ran", "Unexpected withheld information field"
    assert (
        withheld_item["availabilityDate"] == "2025-03-31T00:00:00+01:00"
    ), "Unexpected availability date"


def test_bt198_bt171_unpublished_access_date_missing_data(tmp_path, setup_logging):
    logger = setup_logging
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
          xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
          xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1">
        <efac:noticeResult>
            <efac:LotTender>
                <cbc:ID schemeName="result">TEN-0001</cbc:ID>
                <!-- Missing FieldsPrivacy element -->
            </efac:LotTender>
        </efac:noticeResult>
    </root>
    """
    xml_file = tmp_path / "test_input_bt198_bt171_missing.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open("output.json") as f:
        result = json.load(f)

    logger.info("Result: %s", json.dumps(result, indent=2))

    assert (
        "withheldInformation" not in result
    ), "Did not expect 'withheldInformation' in result when data is missing"


if __name__ == "__main__":
    pytest.main(["-v", "-s"])
