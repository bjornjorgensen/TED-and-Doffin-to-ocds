# tests/test_BT_736_Part.py

import pytest
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main


def test_bt_736_part_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Part">PART-0001</cbc:ID>
            <cac:TenderingTerms>
                <cac:ContractExecutionRequirement>
                    <cbc:ExecutionRequirementCode listName="reserved-execution">yes</cbc:ExecutionRequirementCode>
                </cac:ContractExecutionRequirement>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </root>
    """
    xml_file = tmp_path / "test_input_reserved_execution_part.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open("output.json", "r") as f:
        result = json.load(f)

    assert "tender" in result, "Expected 'tender' in result"
    assert "contractTerms" in result["tender"], "Expected 'contractTerms' in tender"
    assert (
        "reservedExecution" in result["tender"]["contractTerms"]
    ), "Expected 'reservedExecution' in contractTerms"
    assert (
        result["tender"]["contractTerms"]["reservedExecution"] is True
    ), "Expected reservedExecution to be True"


def test_bt_736_part_integration_no_value(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Part">PART-0001</cbc:ID>
            <cac:TenderingTerms>
                <cac:ContractExecutionRequirement>
                    <cbc:ExecutionRequirementCode listName="reserved-execution">no</cbc:ExecutionRequirementCode>
                </cac:ContractExecutionRequirement>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </root>
    """
    xml_file = tmp_path / "test_input_reserved_execution_part_no.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open("output.json", "r") as f:
        result = json.load(f)

    assert "tender" in result, "Expected 'tender' in result"
    assert (
        "contractTerms" not in result["tender"]
        or "reservedExecution" not in result["tender"]["contractTerms"]
    ), "Expected no 'reservedExecution' in contractTerms"


if __name__ == "__main__":
    pytest.main()
