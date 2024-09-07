# tests/test_BT_736_Lot.py

import pytest
from lxml import etree
from converters.BT_736_Lot import parse_reserved_execution, merge_reserved_execution
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main


def test_parse_reserved_execution():
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:TenderingTerms>
                <cac:ContractExecutionRequirement>
                    <cbc:ExecutionRequirementCode listName="reserved-execution">yes</cbc:ExecutionRequirementCode>
                </cac:ContractExecutionRequirement>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </root>
    """

    result = parse_reserved_execution(xml_content)

    assert result is not None
    assert "tender" in result
    assert "lots" in result["tender"]
    assert len(result["tender"]["lots"]) == 1
    assert result["tender"]["lots"][0]["id"] == "LOT-0001"
    assert result["tender"]["lots"][0]["contractTerms"]["reservedExecution"] == True


def test_merge_reserved_execution():
    release_json = {"tender": {"lots": [{"id": "LOT-0001", "title": "Existing Lot"}]}}

    reserved_execution_data = {
        "tender": {
            "lots": [{"id": "LOT-0001", "contractTerms": {"reservedExecution": True}}]
        }
    }

    merge_reserved_execution(release_json, reserved_execution_data)

    assert "contractTerms" in release_json["tender"]["lots"][0]
    assert (
        release_json["tender"]["lots"][0]["contractTerms"]["reservedExecution"] == True
    )


def test_bt_736_lot_reserved_execution_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:TenderingTerms>
                <cac:ContractExecutionRequirement>
                    <cbc:ExecutionRequirementCode listName="reserved-execution">yes</cbc:ExecutionRequirementCode>
                </cac:ContractExecutionRequirement>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0002</cbc:ID>
            <cac:TenderingTerms>
                <cac:ContractExecutionRequirement>
                    <cbc:ExecutionRequirementCode listName="reserved-execution">no</cbc:ExecutionRequirementCode>
                </cac:ContractExecutionRequirement>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </root>
    """
    xml_file = tmp_path / "test_input_reserved_execution.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open("output.json", "r") as f:
        result = json.load(f)

    assert "tender" in result
    assert "lots" in result["tender"]
    assert len(result["tender"]["lots"]) == 2

    lot_1 = next(
        (lot for lot in result["tender"]["lots"] if lot["id"] == "LOT-0001"), None
    )
    assert lot_1 is not None
    assert "contractTerms" in lot_1
    assert lot_1["contractTerms"].get("reservedExecution") == True

    lot_2 = next(
        (lot for lot in result["tender"]["lots"] if lot["id"] == "LOT-0002"), None
    )
    assert lot_2 is not None
    assert "contractTerms" not in lot_2 or "reservedExecution" not in lot_2.get(
        "contractTerms", {}
    )


if __name__ == "__main__":
    pytest.main()
