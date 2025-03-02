# tests/test_opt_300_procedure_buyer.py

import pytest

from src.ted_and_doffin_to_ocds.converters.eforms.opt_300_procedure_buyer import (
    merge_buyer_technical_identifier,
    parse_buyer_technical_identifier,
)


@pytest.fixture
def sample_xml() -> str:
    return """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ContractingParty>
            <cac:Party>
                <cac:PartyIdentification>
                    <cbc:ID>ORG-0001</cbc:ID>
                </cac:PartyIdentification>
            </cac:Party>
        </cac:ContractingParty>
        <cac:ContractingParty>
            <cac:Party>
                <cac:PartyIdentification>
                    <cbc:ID>ORG-0002</cbc:ID>
                </cac:PartyIdentification>
            </cac:Party>
        </cac:ContractingParty>
    </root>
    """


def test_parse_buyer_technical_identifier(sample_xml) -> None:
    result = parse_buyer_technical_identifier(sample_xml)
    assert result is not None
    assert "parties" in result
    assert "buyer" in result
    assert len(result["parties"]) == 2
    assert result["parties"][0]["id"] == "ORG-0001"
    assert result["parties"][0]["roles"] == ["buyer"]
    assert result["parties"][1]["id"] == "ORG-0002"
    assert result["parties"][1]["roles"] == ["buyer"]
    # Check buyer is a single object, not an array
    assert isinstance(result["buyer"], dict)
    assert result["buyer"]["id"] == "ORG-0001"


def test_merge_buyer_technical_identifier() -> None:
    buyer_data = {
        "parties": [
            {"id": "ORG-0001", "roles": ["buyer"]},
            {"id": "ORG-0002", "roles": ["buyer"]},
        ],
        "buyer": {"id": "ORG-0001"},
    }
    release_json = {}
    merge_buyer_technical_identifier(release_json, buyer_data)
    assert "parties" in release_json
    assert "buyer" in release_json
    assert len(release_json["parties"]) == 2
    assert release_json["parties"][0]["id"] == "ORG-0001"
    assert release_json["parties"][0]["roles"] == ["buyer"]
    assert release_json["parties"][1]["id"] == "ORG-0002"
    assert release_json["parties"][1]["roles"] == ["buyer"]
    # Check buyer is a single object, not an array
    assert isinstance(release_json["buyer"], dict)
    assert release_json["buyer"]["id"] == "ORG-0001"


def test_merge_buyer_technical_identifier_existing_party() -> None:
    buyer_data = {
        "parties": [
            {"id": "ORG-0001", "roles": ["buyer"]},
            {"id": "ORG-0002", "roles": ["buyer"]},
        ],
        "buyer": {"id": "ORG-0001"},
    }
    release_json = {
        "parties": [{"id": "ORG-0001", "roles": ["procuringEntity"]}],
        "buyer": {"id": "ORG-0003"},
    }
    merge_buyer_technical_identifier(release_json, buyer_data)
    assert len(release_json["parties"]) == 2
    assert release_json["parties"][0]["id"] == "ORG-0001"
    assert set(release_json["parties"][0]["roles"]) == {"procuringEntity", "buyer"}
    assert release_json["parties"][1]["id"] == "ORG-0002"
    assert release_json["parties"][1]["roles"] == ["buyer"]
    # Buyer should remain unchanged since it already exists
    assert isinstance(release_json["buyer"], dict)
    assert release_json["buyer"]["id"] == "ORG-0003"


def test_parse_buyer_technical_identifier_no_data() -> None:
    xml_content = "<root></root>"
    result = parse_buyer_technical_identifier(xml_content)
    assert result is None


def test_merge_buyer_technical_identifier_no_data() -> None:
    release_json = {}
    merge_buyer_technical_identifier(release_json, None)
    assert release_json == {}
