# tests/test_BT_801_Lot.py

import pytest
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main

def test_bt_801_lot_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:TenderingTerms>
                <cac:ContractExecutionRequirement>
                    <cbc:ExecutionRequirementCode listName="nda">true</cbc:ExecutionRequirementCode>
                </cac:ContractExecutionRequirement>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0002</cbc:ID>
            <cac:TenderingTerms>
                <cac:ContractExecutionRequirement>
                    <cbc:ExecutionRequirementCode listName="nda">false</cbc:ExecutionRequirementCode>
                </cac:ContractExecutionRequirement>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </root>
    """
    xml_file = tmp_path / "test_input_non_disclosure_agreement.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open('output.json', 'r') as f:
        result = json.load(f)

    assert "tender" in result, "Expected 'tender' in result"
    assert "lots" in result["tender"], "Expected 'lots' in result['tender']"
    assert len(result["tender"]["lots"]) == 2, f"Expected 2 lots, got {len(result['tender']['lots'])}"

    lot_1 = next(lot for lot in result["tender"]["lots"] if lot["id"] == "LOT-0001")
    assert "contractTerms" in lot_1, "Expected 'contractTerms' in LOT-0001"
    assert "hasNonDisclosureAgreement" in lot_1["contractTerms"], "Expected 'hasNonDisclosureAgreement' in LOT-0001 contractTerms"
    assert lot_1["contractTerms"]["hasNonDisclosureAgreement"] == True, "Expected hasNonDisclosureAgreement to be True for LOT-0001"

    lot_2 = next(lot for lot in result["tender"]["lots"] if lot["id"] == "LOT-0002")
    assert "contractTerms" in lot_2, "Expected 'contractTerms' in LOT-0002"
    assert "hasNonDisclosureAgreement" in lot_2["contractTerms"], "Expected 'hasNonDisclosureAgreement' in LOT-0002 contractTerms"
    assert lot_2["contractTerms"]["hasNonDisclosureAgreement"] == False, "Expected hasNonDisclosureAgreement to be False for LOT-0002"

if __name__ == "__main__":
    pytest.main()