# tests/test_BT_196_BT_88_Procedure.py

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


def test_bt_196_bt88_procedure_integration(tmp_path, setup_logging):
    logger = setup_logging
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
          xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
          xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1">
        <cbc:ContractFolderID>18d27a53-0109-4f93-9231-6659d931bce0</cbc:ContractFolderID>
        <cac:TenderingProcess>
            <ext:UBLExtensions>
                <ext:UBLExtension>
                    <ext:ExtensionContent>
                        <efext:EformsExtension>
                            <efac:FieldsPrivacy>
                                <efbc:FieldIdentifierCode>pro-fea</efbc:FieldIdentifierCode>
                                <efbc:ReasonDescription>Information delayed publication because of ...</efbc:ReasonDescription>
                            </efac:FieldsPrivacy>
                        </efext:EformsExtension>
                    </ext:ExtensionContent>
                </ext:UBLExtension>
            </ext:UBLExtensions>
        </cac:TenderingProcess>
    </root>
    """
    xml_file = tmp_path / "test_input_bt_196_bt88_procedure.xml"
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

    withheld_item = withheld_info[0]
    assert (
        withheld_item["id"] == "pro-fea-18d27a53-0109-4f93-9231-6659d931bce0"
    ), f"Expected id 'pro-fea-18d27a53-0109-4f93-9231-6659d931bce0', got {withheld_item['id']}"
    assert (
        "rationale" in withheld_item
    ), "Expected 'rationale' in withheld information item"
    assert (
        withheld_item["rationale"] == "Information delayed publication because of ..."
    ), f"Unexpected rationale content: {withheld_item['rationale']}"


def test_bt_196_bt88_procedure_missing_data(tmp_path, setup_logging):
    logger = setup_logging
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID>LOT-0001</cbc:ID>
        </cac:ProcurementProjectLot>
    </root>
    """
    xml_file = tmp_path / "test_input_bt_196_bt88_procedure_missing.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open("output.json") as f:
        result = json.load(f)

    logger.info(f"Result: {json.dumps(result, indent=2)}")

    assert (
        "withheldInformation" not in result
    ), "Did not expect 'withheldInformation' in result when data is missing"


if __name__ == "__main__":
    pytest.main(["-v", "-s"])
