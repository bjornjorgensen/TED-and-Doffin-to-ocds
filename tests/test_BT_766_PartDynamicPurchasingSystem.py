# tests/test_BT_766_PartDynamicPurchasingSystem.py

import pytest
import json
import os
import sys
import logging

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main, configure_logging


def test_bt_766_part_dynamic_purchasing_system_integration(tmp_path):
    configure_logging()
    logger = logging.getLogger(__name__)

    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Part">PART-0001</cbc:ID>
            <cac:TenderingProcess>
                <cac:ContractingSystem>
                    <cbc:ContractingSystemTypeCode listName="dps-usage">dps-nlist</cbc:ContractingSystemTypeCode>
                </cac:ContractingSystem>
            </cac:TenderingProcess>
        </cac:ProcurementProjectLot>
    </root>
    """
    xml_file = tmp_path / "test_input_part_dynamic_purchasing_system.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open("output.json", "r") as f:
        result = json.load(f)

    logger.info(f"Result: {json.dumps(result, indent=2)}")

    assert "tender" in result, "Expected 'tender' in result"
    assert "techniques" in result["tender"], "Expected 'techniques' in tender"
    assert (
        "hasDynamicPurchasingSystem" in result["tender"]["techniques"]
    ), "Expected 'hasDynamicPurchasingSystem' in techniques"
    assert (
        result["tender"]["techniques"]["hasDynamicPurchasingSystem"] is True
    ), "Expected 'hasDynamicPurchasingSystem' to be True"
    assert (
        "dynamicPurchasingSystem" in result["tender"]["techniques"]
    ), "Expected 'dynamicPurchasingSystem' in techniques"
    assert (
        "type" in result["tender"]["techniques"]["dynamicPurchasingSystem"]
    ), "Expected 'type' in dynamicPurchasingSystem"
    assert (
        result["tender"]["techniques"]["dynamicPurchasingSystem"]["type"] == "open"
    ), "Expected type to be 'open'"


def test_bt_766_part_dynamic_purchasing_system_none(tmp_path):
    configure_logging()
    logger = logging.getLogger(__name__)

    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Part">PART-0001</cbc:ID>
            <cac:TenderingProcess>
                <cac:ContractingSystem>
                    <cbc:ContractingSystemTypeCode listName="dps-usage">none</cbc:ContractingSystemTypeCode>
                </cac:ContractingSystem>
            </cac:TenderingProcess>
        </cac:ProcurementProjectLot>
    </root>
    """
    xml_file = tmp_path / "test_input_part_dynamic_purchasing_system_none.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open("output.json", "r") as f:
        result = json.load(f)

    logger.info(f"Result: {json.dumps(result, indent=2)}")

    assert "tender" in result, "Expected 'tender' in result"
    assert (
        "techniques" not in result["tender"]
    ), "Did not expect 'techniques' in tender when DPS usage is 'none'"


if __name__ == "__main__":
    pytest.main(["-v", "-s"])
