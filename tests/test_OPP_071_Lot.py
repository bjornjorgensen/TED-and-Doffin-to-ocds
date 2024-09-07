# tests/test_OPP_071_Lot.py

import pytest
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main


def test_opp_071_lot_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:TenderingTerms>
                <cac:ContractExecutionRequirement>
                    <cbc:ExecutionRequirementCode listName="customer-service">clean</cbc:ExecutionRequirementCode>
                </cac:ContractExecutionRequirement>
                <cac:ContractExecutionRequirement>
                    <cbc:ExecutionRequirementCode listName="customer-service">info</cbc:ExecutionRequirementCode>
                </cac:ContractExecutionRequirement>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </root>
    """
    xml_file = tmp_path / "test_input_quality_target_code.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open("output.json", "r") as f:
        result = json.load(f)

    assert "tender" in result
    assert "lots" in result["tender"]
    assert len(result["tender"]["lots"]) == 1
    lot = result["tender"]["lots"][0]
    assert lot["id"] == "LOT-0001"
    assert "contractTerms" in lot
    assert "customerServices" in lot["contractTerms"]
    assert len(lot["contractTerms"]["customerServices"]) == 2
    assert {
        "type": "clean",
        "name": "Cleanliness of rolling stock and station facilities",
    } in lot["contractTerms"]["customerServices"]
    assert {"type": "info", "name": "Information"} in lot["contractTerms"][
        "customerServices"
    ]


if __name__ == "__main__":
    pytest.main()
