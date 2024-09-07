# tests/test_BT_765_PartFrameworkAgreement.py

import pytest
import json
import os
import sys
import logging

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main, configure_logging


def test_bt_765_part_framework_agreement_integration(tmp_path):
    configure_logging()
    logger = logging.getLogger(__name__)

    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Part">PART-0001</cbc:ID>
            <cac:TenderingProcess>
                <cac:ContractingSystem>
                    <cbc:ContractingSystemTypeCode listName="framework-agreement">fa-wo-rc</cbc:ContractingSystemTypeCode>
                </cac:ContractingSystem>
            </cac:TenderingProcess>
        </cac:ProcurementProjectLot>
    </root>
    """
    xml_file = tmp_path / "test_input_part_framework_agreement.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open("output.json", "r") as f:
        result = json.load(f)

    logger.info(f"Result: {json.dumps(result, indent=2)}")

    assert "tender" in result, "Expected 'tender' in result"
    assert "techniques" in result["tender"], "Expected 'techniques' in tender"
    assert (
        "hasFrameworkAgreement" in result["tender"]["techniques"]
    ), "Expected 'hasFrameworkAgreement' in techniques"
    assert (
        result["tender"]["techniques"]["hasFrameworkAgreement"] is True
    ), "Expected 'hasFrameworkAgreement' to be True"
    assert (
        "frameworkAgreement" in result["tender"]["techniques"]
    ), "Expected 'frameworkAgreement' in techniques"
    assert (
        "method" in result["tender"]["techniques"]["frameworkAgreement"]
    ), "Expected 'method' in frameworkAgreement"
    assert (
        result["tender"]["techniques"]["frameworkAgreement"]["method"]
        == "withoutReopeningCompetition"
    ), "Expected method to be 'withoutReopeningCompetition'"


def test_bt_765_part_framework_agreement_none(tmp_path):
    configure_logging()
    logger = logging.getLogger(__name__)

    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Part">PART-0001</cbc:ID>
            <cac:TenderingProcess>
                <cac:ContractingSystem>
                    <cbc:ContractingSystemTypeCode listName="framework-agreement">none</cbc:ContractingSystemTypeCode>
                </cac:ContractingSystem>
            </cac:TenderingProcess>
        </cac:ProcurementProjectLot>
    </root>
    """
    xml_file = tmp_path / "test_input_part_framework_agreement_none.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open("output.json", "r") as f:
        result = json.load(f)

    logger.info(f"Result: {json.dumps(result, indent=2)}")

    assert "tender" in result, "Expected 'tender' in result"
    assert (
        "techniques" not in result["tender"]
    ), "Did not expect 'techniques' in tender when framework agreement is 'none'"


if __name__ == "__main__":
    pytest.main(["-v", "-s"])
