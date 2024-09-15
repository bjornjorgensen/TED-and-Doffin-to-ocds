# tests/test_BT_198_BT_733_LotsGroup.py

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


def test_bt_198_bt733_lotsgroup_integration(tmp_path, setup_logging):
    logger = setup_logging
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
          xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
          xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="LotsGroup">GLO-0001</cbc:ID>
            <cac:TenderingTerms>
                <cac:AwardingTerms>
                    <cac:AwardingCriterion>
                        <ext:UBLExtensions>
                            <ext:UBLExtension>
                                <ext:ExtensionContent>
                                    <efext:EformsExtension>
                                        <efac:FieldsPrivacy>
                                            <efbc:FieldIdentifierCode>awa-cri-ord</efbc:FieldIdentifierCode>
                                            <efbc:PublicationDate>2025-03-31+01:00</efbc:PublicationDate>
                                        </efac:FieldsPrivacy>
                                    </efext:EformsExtension>
                                </ext:ExtensionContent>
                            </ext:UBLExtension>
                        </ext:UBLExtensions>
                    </cac:AwardingCriterion>
                </cac:AwardingTerms>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </root>
    """
    xml_file = tmp_path / "test_input_bt198_bt733_lotsgroup.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open("output.json") as f:
        result = json.load(f)

    logger.info(f"Result: {json.dumps(result, indent=2)}")

    assert "withheldInformation" in result, "Expected 'withheldInformation' in result"
    assert (
        len(result["withheldInformation"]) == 1
    ), f"Expected 1 withheld information item, got {len(result['withheldInformation'])}"

    withheld_info = result["withheldInformation"][0]
    assert (
        withheld_info["id"] == "awa-cri-ord-GLO-0001"
    ), "Unexpected withheld information id"
    assert (
        withheld_info["field"] == "awa-cri-ord"
    ), "Unexpected withheld information field"
    assert (
        withheld_info["availabilityDate"] == "2025-03-31T00:00:00+01:00"
    ), "Unexpected withheld information availability date"


def test_bt_198_bt733_lotsgroup_missing_field(tmp_path, setup_logging):
    logger = setup_logging
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
          xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
          xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="LotsGroup">GLO-0001</cbc:ID>
        </cac:ProcurementProjectLot>
    </root>
    """
    xml_file = tmp_path / "test_input_bt198_bt733_lotsgroup_missing.xml"
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
