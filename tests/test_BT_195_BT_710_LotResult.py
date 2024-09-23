# tests/test_bt_195_bt_710_LotResult.py

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


def test_bt_195_bt710_lot_result_integration(tmp_path, setup_logging):
    logger = setup_logging
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
          xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
          xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1">
        <efac:noticeResult>
            <efac:LotResult>
                <efac:FieldsPrivacy>
                    <efbc:FieldIdentifierCode>ten-val-low</efbc:FieldIdentifierCode>
                </efac:FieldsPrivacy>
                <cbc:ID schemeName="result">RES-0001</cbc:ID>
            </efac:LotResult>
            <efac:LotResult>
                <efac:FieldsPrivacy>
                    <efbc:FieldIdentifierCode>ten-val-low</efbc:FieldIdentifierCode>
                </efac:FieldsPrivacy>
                <cbc:ID schemeName="result">RES-0002</cbc:ID>
            </efac:LotResult>
        </efac:noticeResult>
    </root>
    """
    xml_file = tmp_path / "test_input_bt195_bt710.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open("output.json") as f:
        result = json.load(f)

    logger.info(f"Result: {json.dumps(result, indent=2)}")

    assert "withheldInformation" in result, "Expected 'withheldInformation' in result"
    assert (
        len(result["withheldInformation"]) == 2
    ), f"Expected 2 withheld information items, got {len(result['withheldInformation'])}"

    expected_withheld_info = [
        {
            "id": "ten-val-low-RES-0001",
            "field": "ten-val-low",
            "name": "Tender Lowest Value",
        },
        {
            "id": "ten-val-low-RES-0002",
            "field": "ten-val-low",
            "name": "Tender Lowest Value",
        },
    ]

    assert (
        result["withheldInformation"] == expected_withheld_info
    ), "Unexpected withheld information content"


def test_bt_195_bt710_lot_result_missing_field(tmp_path, setup_logging):
    logger = setup_logging
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
          xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
          xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1">
        <efac:noticeResult>
            <efac:LotResult>
                <cbc:ID schemeName="result">RES-0001</cbc:ID>
            </efac:LotResult>
        </efac:noticeResult>
    </root>
    """
    xml_file = tmp_path / "test_input_bt195_bt710_missing.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open("output.json") as f:
        result = json.load(f)

    logger.info(f"Result: {json.dumps(result, indent=2)}")

    assert (
        "withheldInformation" not in result
        or len(result.get("withheldInformation", [])) == 0
    ), "Did not expect 'withheldInformation' when FieldsPrivacy is missing"


if __name__ == "__main__":
    pytest.main(["-v", "-s"])
