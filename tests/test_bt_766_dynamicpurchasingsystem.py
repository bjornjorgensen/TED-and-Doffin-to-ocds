# tests/test_bt_766_DynamicPurchasingSystem.py

import pytest
import json
import os
import sys
import logging

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.ted_and_doffin_to_ocds.main import main, configure_logging


def test_bt_766_dynamic_purchasing_system_integration(tmp_path):
    configure_logging()
    logger = logging.getLogger(__name__)

    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:TenderingProcess>
                <cac:ContractingSystem>
                    <cbc:ContractingSystemTypeCode listName="dps-usage">dps-nlist</cbc:ContractingSystemTypeCode>
                </cac:ContractingSystem>
            </cac:TenderingProcess>
        </cac:ProcurementProjectLot>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0002</cbc:ID>
            <cac:TenderingProcess>
                <cac:ContractingSystem>
                    <cbc:ContractingSystemTypeCode listName="dps-usage">dps-list</cbc:ContractingSystemTypeCode>
                </cac:ContractingSystem>
            </cac:TenderingProcess>
        </cac:ProcurementProjectLot>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0003</cbc:ID>
            <cac:TenderingProcess>
                <cac:ContractingSystem>
                    <cbc:ContractingSystemTypeCode listName="dps-usage">none</cbc:ContractingSystemTypeCode>
                </cac:ContractingSystem>
            </cac:TenderingProcess>
        </cac:ProcurementProjectLot>
    </root>
    """
    xml_file = tmp_path / "test_input_dynamic_purchasing_system.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open("output.json") as f:
        result = json.load(f)

    logger.info("Result: %s", json.dumps(result, indent=2))

    assert "tender" in result, "Expected 'tender' in result"
    assert "lots" in result["tender"], "Expected 'lots' in tender"
    assert (
        len(result["tender"]["lots"]) == 2
    ), f"Expected 2 lots with dynamic purchasing system, got {len(result['tender']['lots'])}"

    expected_types = {"LOT-0001": "open", "LOT-0002": "closed"}

    for lot in result["tender"]["lots"]:
        assert lot["id"] in expected_types, f"Unexpected lot {lot['id']} in result"
        assert "techniques" in lot, f"Expected 'techniques' in lot {lot['id']}"
        assert (
            "hasDynamicPurchasingSystem" in lot["techniques"]
        ), f"Expected 'hasDynamicPurchasingSystem' in lot {lot['id']} techniques"
        assert (
            lot["techniques"]["hasDynamicPurchasingSystem"] is True
        ), f"Expected 'hasDynamicPurchasingSystem' to be True for lot {lot['id']}"
        assert (
            "dynamicPurchasingSystem" in lot["techniques"]
        ), f"Expected 'dynamicPurchasingSystem' in lot {lot['id']} techniques"
        assert (
            "type" in lot["techniques"]["dynamicPurchasingSystem"]
        ), f"Expected 'type' in lot {lot['id']} dynamicPurchasingSystem"
        assert (
            lot["techniques"]["dynamicPurchasingSystem"]["type"]
            == expected_types[lot["id"]]
        ), f"Expected type {expected_types[lot['id']]} for lot {lot['id']}, got {lot['techniques']['dynamicPurchasingSystem']['type']}"

    assert "LOT-0003" not in [
        lot["id"] for lot in result["tender"]["lots"]
    ], "LOT-0003 should not be included in the result"


if __name__ == "__main__":
    pytest.main(["-v", "-s"])
