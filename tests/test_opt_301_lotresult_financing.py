# tests/test_opt_301_lotresult_financing.py

from src.ted_and_doffin_to_ocds.converters.eforms.opt_301_lotresult_financing import (
    merge_financing_party,
    parse_financing_party,
)


def test_parse_financing_party() -> None:
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
          xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1">
        <efac:NoticeResult>
            <efac:LotResult>
                <cac:FinancingParty>
                    <cac:PartyIdentification>
                        <cbc:ID schemeName="organization">ORG-0003</cbc:ID>
                    </cac:PartyIdentification>
                </cac:FinancingParty>
            </efac:LotResult>
        </efac:NoticeResult>
    </root>
    """

    result = parse_financing_party(xml_content)

    assert result is not None
    assert "parties" in result
    assert len(result["parties"]) == 1

    party = result["parties"][0]
    assert party["id"] == "ORG-0003"
    assert party["roles"] == ["funder"]


def test_merge_financing_party() -> None:
    release_json = {"parties": []}
    financing_party_data = {"parties": [{"id": "ORG-0003", "roles": ["funder"]}]}

    merge_financing_party(release_json, financing_party_data)

    assert "parties" in release_json
    assert len(release_json["parties"]) == 1

    party = release_json["parties"][0]
    assert party["id"] == "ORG-0003"
    assert party["roles"] == ["funder"]


def test_merge_financing_party_existing_party() -> None:
    release_json = {
        "parties": [
            {"id": "ORG-0003", "name": "Existing Organization", "roles": ["buyer"]}
        ]
    }
    financing_party_data = {"parties": [{"id": "ORG-0003", "roles": ["funder"]}]}

    merge_financing_party(release_json, financing_party_data)

    assert len(release_json["parties"]) == 1

    party = release_json["parties"][0]
    assert party["id"] == "ORG-0003"
    assert party["name"] == "Existing Organization"
    assert set(party["roles"]) == {"buyer", "funder"}
