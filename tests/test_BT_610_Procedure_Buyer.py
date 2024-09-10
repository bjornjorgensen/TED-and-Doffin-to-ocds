# tests/test_BT_610_Procedure_Buyer.py

import pytest
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.ted_and_doffin_to_ocds.main import main


def test_bt_610_procedure_buyer_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ContractingParty>
            <cac:ContractingActivity>
                <cbc:ActivityTypeCode listName="entity-activity">gas-oil</cbc:ActivityTypeCode>
            </cac:ContractingActivity>
            <cac:Party>
                <cac:PartyIdentification>
                    <cbc:ID>ORG-0001</cbc:ID>
                </cac:PartyIdentification>
            </cac:Party>
        </cac:ContractingParty>
    </root>
    """
    xml_file = tmp_path / "test_input_activity_entity.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open("output.json") as f:
        result = json.load(f)

    assert "parties" in result, "Expected 'parties' in result"
    assert (
        len(result["parties"]) == 1
    ), f"Expected 1 party, got {len(result['parties'])}"

    party = result["parties"][0]
    assert party["id"] == "ORG-0001", f"Expected party id 'ORG-0001', got {party['id']}"
    assert "buyer" in party["roles"], "Expected 'buyer' in party roles"
    assert "details" in party, "Expected 'details' in party"
    assert (
        "classifications" in party["details"]
    ), "Expected 'classifications' in party details"
    assert (
        len(party["details"]["classifications"]) == 1
    ), f"Expected 1 classification, got {len(party['details']['classifications'])}"

    classification = party["details"]["classifications"][0]
    assert (
        classification["scheme"] == "eu-main-activity"
    ), f"Expected scheme 'eu-main-activity', got {classification['scheme']}"
    assert (
        classification["id"] == "gas-oil"
    ), f"Expected id 'gas-oil', got {classification['id']}"
    assert (
        classification["description"] == "Extraction of gas or oil"
    ), f"Expected description 'Extraction of gas or oil', got {classification['description']}"


if __name__ == "__main__":
    pytest.main()
