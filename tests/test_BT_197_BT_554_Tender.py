# tests/test_bt_197_bt_554_Tender.py

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


def test_bt_197_bt554_tender_integration(tmp_path, setup_logging):
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
                <efac:SubcontractingTerm>
                    <efbc:TermCode listName="applicability">applicable</efbc:TermCode>
                    <efac:FieldsPrivacy>
                        <efbc:FieldIdentifierCode>sub-des</efbc:FieldIdentifierCode>
                        <cbc:ReasonCode listName="non-publication-justification">oth-int</cbc:ReasonCode>
                    </efac:FieldsPrivacy>
                </efac:SubcontractingTerm>
            </efac:LotTender>
        </efac:noticeResult>
    </root>
    """
    xml_file = tmp_path / "test_input_bt197_bt554.xml"
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
        item["id"] == "sub-des-TEN-0001"
    ), f"Expected id 'sub-des-TEN-0001', got {item['id']}"
    assert (
        "rationaleClassifications" in item
    ), "Expected 'rationaleClassifications' in withheld information item"
    assert (
        len(item["rationaleClassifications"]) == 1
    ), "Expected 1 rationaleClassification"

    classification = item["rationaleClassifications"][0]
    assert (
        classification["scheme"] == "eu-non-publication-justification"
    ), "Unexpected scheme"
    assert classification["id"] == "oth-int", "Unexpected id"
    assert (
        classification["description"] == "Other public interest"
    ), "Unexpected description"
    assert (
        classification["uri"]
        == "http://publications.europa.eu/resource/authority/non-publication-justification/oth-int"
    ), "Unexpected URI"


if __name__ == "__main__":
    pytest.main(["-v", "-s"])
