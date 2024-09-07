# tests/test_BT_765_FrameworkAgreement.py

import pytest
import json
import os
import sys
import logging

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main, configure_logging


def test_bt_765_framework_agreement_integration(tmp_path):
    configure_logging()
    logger = logging.getLogger(__name__)

    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:TenderingProcess>
                <cac:ContractingSystem>
                    <cbc:ContractingSystemTypeCode listName="framework-agreement">fa-wo-rc</cbc:ContractingSystemTypeCode>
                </cac:ContractingSystem>
            </cac:TenderingProcess>
        </cac:ProcurementProjectLot>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0002</cbc:ID>
            <cac:TenderingProcess>
                <cac:ContractingSystem>
                    <cbc:ContractingSystemTypeCode listName="framework-agreement">fa-w-rc</cbc:ContractingSystemTypeCode>
                </cac:ContractingSystem>
            </cac:TenderingProcess>
        </cac:ProcurementProjectLot>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0003</cbc:ID>
            <cac:TenderingProcess>
                <cac:ContractingSystem>
                    <cbc:ContractingSystemTypeCode listName="framework-agreement">fa-mix</cbc:ContractingSystemTypeCode>
                </cac:ContractingSystem>
            </cac:TenderingProcess>
        </cac:ProcurementProjectLot>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0004</cbc:ID>
            <cac:TenderingProcess>
                <cac:ContractingSystem>
                    <cbc:ContractingSystemTypeCode listName="framework-agreement">none</cbc:ContractingSystemTypeCode>
                </cac:ContractingSystem>
            </cac:TenderingProcess>
        </cac:ProcurementProjectLot>
    </root>
    """
    xml_file = tmp_path / "test_input_framework_agreement.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open("output.json", "r") as f:
        result = json.load(f)

    logger.info(f"Result: {json.dumps(result, indent=2)}")

    assert "tender" in result, "Expected 'tender' in result"
    assert "lots" in result["tender"], "Expected 'lots' in tender"
    assert (
        len(result["tender"]["lots"]) == 3
    ), f"Expected 3 lots with framework agreements, got {len(result['tender']['lots'])}"

    expected_methods = {
        "LOT-0001": "withoutReopeningCompetition",
        "LOT-0002": "withReopeningCompetition",
        "LOT-0003": "withAndWithoutReopeningCompetition",
    }

    for lot in result["tender"]["lots"]:
        assert lot["id"] in expected_methods, f"Unexpected lot {lot['id']} in result"
        assert "techniques" in lot, f"Expected 'techniques' in lot {lot['id']}"
        assert (
            "hasFrameworkAgreement" in lot["techniques"]
        ), f"Expected 'hasFrameworkAgreement' in lot {lot['id']} techniques"
        assert (
            lot["techniques"]["hasFrameworkAgreement"] is True
        ), f"Expected 'hasFrameworkAgreement' to be True for lot {lot['id']}"
        assert (
            "frameworkAgreement" in lot["techniques"]
        ), f"Expected 'frameworkAgreement' in lot {lot['id']} techniques"
        assert (
            "method" in lot["techniques"]["frameworkAgreement"]
        ), f"Expected 'method' in lot {lot['id']} frameworkAgreement"
        assert (
            lot["techniques"]["frameworkAgreement"]["method"]
            == expected_methods[lot["id"]]
        ), f"Expected method {expected_methods[lot['id']]} for lot {lot['id']}, got {lot['techniques']['frameworkAgreement']['method']}"

    assert "LOT-0004" not in [
        lot["id"] for lot in result["tender"]["lots"]
    ], "LOT-0004 should not be included in the result"


if __name__ == "__main__":
    pytest.main(["-v", "-s"])
