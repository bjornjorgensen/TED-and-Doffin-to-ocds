# tests/test_bt_11_procedure_buyer.py
from pathlib import Path
import pytest
import json
import sys

sys.path.append(str(Path(__file__).parent.parent))
from src.ted_and_doffin_to_ocds.main import main


def test_bt_11_procedure_buyer_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:Contractingparty>
            <cac:party>
                <cac:partyIdentification>
                    <cbc:ID schemeName="organization">ORG-0001</cbc:ID>
                </cac:partyIdentification>
            </cac:party>
            <cac:ContractingpartyType>
                <cbc:partyTypeCode listName="buyer-legal-type">body-pl</cbc:partyTypeCode>
            </cac:ContractingpartyType>
        </cac:Contractingparty>
    </root>
    """
    xml_file = tmp_path / "test_input_buyer_legal_type.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with Path("output.json").open() as f:
        result = json.load(f)

    assert "parties" in result
    assert len(result["parties"]) == 1
    party = result["parties"][0]
    assert party["id"] == "ORG-0001"
    assert "details" in party
    assert "classifications" in party["details"]
    assert len(party["details"]["classifications"]) == 1
    classification = party["details"]["classifications"][0]
    assert classification["scheme"] == "TED_CA_TYPE"
    assert classification["id"] == "body-pl"
    assert classification["description"] == "Body governed by public law"


if __name__ == "__main__":
    pytest.main()
