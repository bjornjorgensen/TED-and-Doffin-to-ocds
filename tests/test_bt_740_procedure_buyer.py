# tests/test_bt_740_procedure_buyer.py

import pytest
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.ted_and_doffin_to_ocds.main import main


def test_bt_740_procedure_buyer_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ContractingpartyType>
            <cac:party>
                <cac:partyIdentification>
                    <cbc:ID>ORG-0001</cbc:ID>
                </cac:partyIdentification>
            </cac:party>
            <cbc:partyTypeCode listName="buyer-contracting-type">cont-ent</cbc:partyTypeCode>
        </cac:ContractingpartyType>
    </root>
    """
    xml_file = tmp_path / "test_input_buyer_contracting_entity.xml"
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
    assert "details" in party, "Expected 'details' in party"
    assert (
        "classifications" in party["details"]
    ), "Expected 'classifications' in party details"
    assert (
        len(party["details"]["classifications"]) == 1
    ), f"Expected 1 classification, got {len(party['details']['classifications'])}"

    classification = party["details"]["classifications"][0]
    assert (
        classification["scheme"] == "eu-buyer-contracting-type"
    ), f"Expected scheme 'eu-buyer-contracting-type', got {classification['scheme']}"
    assert (
        classification["id"] == "cont-ent"
    ), f"Expected id 'cont-ent', got {classification['id']}"
    assert (
        classification["description"] == "Contracting Entity"
    ), f"Expected description 'Contracting Entity', got {classification['description']}"

    assert "roles" in party, "Expected 'roles' in party"
    assert "buyer" in party["roles"], "Expected 'buyer' in party roles"


if __name__ == "__main__":
    pytest.main()
