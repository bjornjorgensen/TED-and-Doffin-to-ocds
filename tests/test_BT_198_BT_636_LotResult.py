# tests/test_BT_198_BT_636_LotResult.py

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


def test_bt_198_bt636_lotresult_integration(tmp_path, setup_logging):
    logger = setup_logging
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
          xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
          xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1">
        <efac:NoticeResult>
            <efac:LotResult>
                <cbc:ID schemeName="result">RES-0001</cbc:ID>
                <efac:AppealRequestsStatistics>
                    <efbc:StatisticsCode listName="irregularity-type">total</efbc:StatisticsCode>
                    <efac:FieldsPrivacy>
                        <efbc:FieldIdentifierCode>buy-rev-typ</efbc:FieldIdentifierCode>
                        <efbc:PublicationDate>2025-03-31+01:00</efbc:PublicationDate>
                    </efac:FieldsPrivacy>
                </efac:AppealRequestsStatistics>
            </efac:LotResult>
        </efac:NoticeResult>
    </root>
    """
    xml_file = tmp_path / "test_input_bt198_bt636.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open("output.json") as f:
        result = json.load(f)

    logger.info(f"Result: {json.dumps(result, indent=2)}")

    assert "withheldInformation" in result, "Expected 'withheldInformation' in result"
    withheld_info = result["withheldInformation"]
    assert (
        len(withheld_info) == 1
    ), f"Expected 1 withheld information item, got {len(withheld_info)}"

    item = withheld_info[0]
    assert (
        item["id"] == "buy-rev-typ-RES-0001"
    ), f"Expected id 'buy-rev-typ-RES-0001', got {item['id']}"
    assert (
        "availabilityDate" in item
    ), "Expected 'availabilityDate' in withheld information item"
    assert (
        item["availabilityDate"] == "2025-03-31T00:00:00+01:00"
    ), f"Unexpected availabilityDate: {item['availabilityDate']}"


if __name__ == "__main__":
    pytest.main(["-v", "-s"])
