# tests/test_BT_802_Lot.py

import pytest
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main

def test_bt_802_lot_non_disclosure_agreement_description_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:TenderingTerms>
                <cac:ContractExecutionRequirement>
                    <cbc:ExecutionRequirementCode listName="nda">true</cbc:ExecutionRequirementCode>
                    <cbc:Description>A Non Disclosure Agreement will need to be signed.</cbc:Description>
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
    xml_file = tmp_path / "test_input_non_disclosure_agreement_description.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open('output.json', 'r') as f:
        result = json.load(f)

    assert "tender" in result
    assert "lots" in result["tender"]
    
    nda_lots = [lot for lot in result["tender"]["lots"] if "contractTerms" in lot and "nonDisclosureAgreement" in lot["contractTerms"]]
    assert len(nda_lots) == 1

    lot_1 = nda_lots[0]
    assert lot_1["id"] == "LOT-0001"
    assert lot_1["contractTerms"]["nonDisclosureAgreement"] == "A Non Disclosure Agreement will need to be signed."

    lot_2 = next((lot for lot in result["tender"]["lots"] if lot["id"] == "LOT-0002"), None)
    assert lot_2 is not None
    assert "contractTerms" not in lot_2 or "nonDisclosureAgreement" not in lot_2.get("contractTerms", {})

if __name__ == "__main__":
    pytest.main()