# tests/test_OPT_300_Procedure_Buyer.py

import pytest
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main

def test_opt_300_procedure_buyer_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ContractingParty>
            <cac:Party>
                <cac:PartyIdentification>
                    <cbc:ID>ORG-0001</cbc:ID>
                </cac:PartyIdentification>
            </cac:Party>
        </cac:ContractingParty>
    </root>
    """
    xml_file = tmp_path / "test_input_procedure_buyer.xml"
    xml_file.write_text(xml_content)

    result = main(str(xml_file), "ocds-test-prefix")

    assert result is not None
    assert "parties" in result
    assert len(result["parties"]) == 1
    party = result["parties"][0]
    assert party["id"] == "ORG-0001"
    assert "buyer" in party["roles"]

    assert "buyer" in result
    assert result["buyer"]["id"] == "ORG-0001"

if __name__ == "__main__":
    pytest.main()