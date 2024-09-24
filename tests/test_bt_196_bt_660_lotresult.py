# tests/test_bt_196_bt_660_LotResult.py

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


def test_bt_196_bt660_lotresult_integration(tmp_path, setup_logging):
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
                <efac:FrameworkAgreementValues>
                    <efac:FieldsPrivacy>
                        <efbc:FieldIdentifierCode>ree-val</efbc:FieldIdentifierCode>
                        <efbc:ReasonDescription languageID="ENG">Information delayed publication because of ...</efbc:ReasonDescription>
                    </efac:FieldsPrivacy>
                </efac:FrameworkAgreementValues>
            </efac:LotResult>
        </efac:noticeResult>
    </root>
    """
    xml_file = tmp_path / "test_input_bt196_bt660.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open("output.json") as f:
        result = json.load(f)

    logger.info("Result: %s", json.dumps(result, indent=2))

    assert "withheldInformation" in result, "Expected 'withheldInformation' in result"
    withheld_info = result["withheldInformation"]
    assert (
        len(withheld_info) == 1
    ), f"Expected 1 withheld information item, got {len(withheld_info)}"

    item = withheld_info[0]
    assert (
        item["id"] == "ree-val-RES-0001"
    ), f"Expected id 'ree-val-RES-0001', got {item['id']}"
    assert "rationale" in item, "Expected 'rationale' in withheld information item"
    assert (
        item["rationale"] == "Information delayed publication because of ..."
    ), "Unexpected rationale content"


if __name__ == "__main__":
    pytest.main(["-v", "-s"])
