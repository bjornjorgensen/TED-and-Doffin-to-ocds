# tests/test_opt_301_lotresult_paying.py

from src.ted_and_doffin_to_ocds.converters.eforms.opt_301_lotresult_paying import (
    merge_payer_party,
    parse_payer_party,
)


def test_parse_payer_party() -> None:
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
          xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1">
        <efac:NoticeResult>
            <efac:LotResult>
                <cac:PayerParty>
                    <cac:PartyIdentification>
                        <cbc:ID schemeName="organization">ORG-0001</cbc:ID>
                    </cac:PartyIdentification>
                </cac:PayerParty>
            </efac:LotResult>
        </efac:NoticeResult>
    </root>
    """

    result = parse_payer_party(xml_content)

    assert result is not None
    assert "parties" in result
    assert len(result["parties"]) == 1

    party = result["parties"][0]
    assert party["id"] == "ORG-0001"
    assert party["roles"] == ["payer"]


def test_merge_payer_party() -> None:
    release_json = {"parties": []}
    payer_party_data = {"parties": [{"id": "ORG-0001", "roles": ["payer"]}]}

    merge_payer_party(release_json, payer_party_data)

    assert "parties" in release_json
    assert len(release_json["parties"]) == 1

    party = release_json["parties"][0]
    assert party["id"] == "ORG-0001"
    assert party["roles"] == ["payer"]


def test_merge_payer_party_existing_party() -> None:
    release_json = {
        "parties": [
            {"id": "ORG-0001", "name": "Existing Organization", "roles": ["buyer"]}
        ]
    }
    payer_party_data = {"parties": [{"id": "ORG-0001", "roles": ["payer"]}]}

    merge_payer_party(release_json, payer_party_data)

    assert len(release_json["parties"]) == 1

    party = release_json["parties"][0]
    assert party["id"] == "ORG-0001"
    assert party["name"] == "Existing Organization"
    assert set(party["roles"]) == {"buyer", "payer"}
