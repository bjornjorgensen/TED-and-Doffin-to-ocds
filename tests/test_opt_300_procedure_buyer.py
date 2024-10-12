# tests/test_opt_300_procedure_buyer.py

import pytest
from ted_and_doffin_to_ocds.converters.opt_300_procedure_buyer import (
    parse_buyer_technical_identifier,
    merge_buyer_technical_identifier,
)


@pytest.fixture
def sample_xml():
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


def test_parse_buyer_technical_identifier(sample_xml):
    result = parse_buyer_technical_identifier(sample_xml)
    assert result is not None
    assert "parties" in result
    assert "buyer" in result
    assert len(result["parties"]) == 2
    assert result["parties"][0]["id"] == "ORG-0001"
    assert result["parties"][0]["roles"] == ["buyer"]
    assert result["parties"][1]["id"] == "ORG-0002"
    assert result["parties"][1]["roles"] == ["buyer"]
    assert len(result["buyer"]) == 2
    assert result["buyer"][0]["id"] == "ORG-0001"
    assert result["buyer"][1]["id"] == "ORG-0002"


def test_merge_buyer_technical_identifier():
    buyer_data = {
        "parties": [
            {"id": "ORG-0001", "roles": ["buyer"]},
            {"id": "ORG-0002", "roles": ["buyer"]},
        ],
        "buyer": [{"id": "ORG-0001"}, {"id": "ORG-0002"}],
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
    assert len(release_json["buyer"]) == 2
    assert release_json["buyer"][0]["id"] == "ORG-0001"
    assert release_json["buyer"][1]["id"] == "ORG-0002"


def test_merge_buyer_technical_identifier_existing_party():
    buyer_data = {
        "parties": [
            {"id": "ORG-0001", "roles": ["buyer"]},
            {"id": "ORG-0002", "roles": ["buyer"]},
        ],
        "buyer": [{"id": "ORG-0001"}, {"id": "ORG-0002"}],
    }
    release_json = {
        "parties": [{"id": "ORG-0001", "roles": ["procuringEntity"]}],
        "buyer": [{"id": "ORG-0003"}],
    }
    merge_buyer_technical_identifier(release_json, buyer_data)
    assert len(release_json["parties"]) == 2
    assert release_json["parties"][0]["id"] == "ORG-0001"
    assert set(release_json["parties"][0]["roles"]) == {"procuringEntity", "buyer"}
    assert release_json["parties"][1]["id"] == "ORG-0002"
    assert release_json["parties"][1]["roles"] == ["buyer"]
    assert len(release_json["buyer"]) == 3
    assert {"id": "ORG-0001"} in release_json["buyer"]
    assert {"id": "ORG-0002"} in release_json["buyer"]
    assert {"id": "ORG-0003"} in release_json["buyer"]


def test_parse_buyer_technical_identifier_no_data():
    xml_content = "<root></root>"
    result = parse_buyer_technical_identifier(xml_content)
    assert result is None


def test_merge_buyer_technical_identifier_no_data():
    release_json = {}
    merge_buyer_technical_identifier(release_json, None)
    assert release_json == {}
