# tests/test_bt_197_bt_191_Tender.py
from pathlib import Path
import pytest
import json
import sys
import logging

# Add the parent directory to sys.path to import main
sys.path.append(str(Path(__file__).parent.parent))
from src.ted_and_doffin_to_ocds.main import main, configure_logging


@pytest.fixture(scope="module")
def setup_logging():
    configure_logging()
    return logging.getLogger(__name__)


def test_bt197_bt191_unpublished_justification_code_integration(
    tmp_path,
    setup_logging,
):
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
                <efac:Origin>
                    <efac:FieldsPrivacy>
                        <efbc:FieldIdentifierCode>cou-ori</efbc:FieldIdentifierCode>
                        <cbc:ReasonCode listName="non-publication-justification">oth-int</cbc:ReasonCode>
                    </efac:FieldsPrivacy>
                </efac:Origin>
            </efac:LotTender>
        </efac:noticeResult>
    </root>
    """
    xml_file = tmp_path / "test_input_bt197_bt191.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with Path("output.json").open() as f:
        result = json.load(f)

    logger.info("Result: %s", json.dumps(result, indent=2))

    assert "withheldInformation" in result, "Expected 'withheldInformation' in result"
    assert (
        len(result["withheldInformation"]) == 1
    ), "Expected one withheld information item"

    withheld_item = result["withheldInformation"][0]
    assert (
        withheld_item["id"] == "cou-ori-TEN-0001"
    ), "Unexpected withheld information id"
    assert withheld_item["field"] == "cou-ori", "Unexpected withheld information field"
    assert (
        "rationaleClassifications" in withheld_item
    ), "Expected 'rationaleClassifications' in withheld item"
    assert (
        len(withheld_item["rationaleClassifications"]) == 1
    ), "Expected one rationale classification"

    classification = withheld_item["rationaleClassifications"][0]
    assert (
        classification["scheme"] == "eu-non-publication-justification"
    ), "Unexpected classification scheme"
    assert classification["id"] == "oth-int", "Unexpected classification id"
    assert (
        classification["description"] == "Other public interest"
    ), "Unexpected classification description"
    assert (
        classification["uri"]
        == "http://publications.europa.eu/resource/authority/non-publication-justification/oth-int"
    ), "Unexpected classification uri"


def test_bt197_bt191_unpublished_justification_code_missing_data(
    tmp_path,
    setup_logging,
):
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
                <!-- Missing Origin element -->
            </efac:LotTender>
        </efac:noticeResult>
    </root>
    """
    xml_file = tmp_path / "test_input_bt197_bt191_missing.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with Path("output.json").open() as f:
        result = json.load(f)

    logger.info("Result: %s", json.dumps(result, indent=2))

    assert (
        "withheldInformation" not in result
    ), "Did not expect 'withheldInformation' in result when data is missing"


if __name__ == "__main__":
    pytest.main(["-v", "-s"])
