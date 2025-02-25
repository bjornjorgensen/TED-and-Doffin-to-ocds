# tests/test_opt_300_contract_signatory.py

from src.ted_and_doffin_to_ocds.converters.eforms.opt_300_contract_signatory import (
    merge_signatory_identifier_reference,
    parse_signatory_identifier_reference,
)


def test_parse_signatory_identifier_reference() -> None:
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
          xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1">
        <efext:EformsExtension>
            <efac:Organizations>
                <efac:Organization>
                    <efac:Company>
                        <cac:PartyIdentification>
                            <cbc:ID schemeName="organization">ORG-0001</cbc:ID>
                        </cac:PartyIdentification>
                        <cac:PartyName>
                            <cbc:Name languageID="ENG">Financial Administration for ...</cbc:Name>
                        </cac:PartyName>
                    </efac:Company>
                </efac:Organization>
            </efac:Organizations>
            <efac:NoticeResult>
                <efac:SettledContract>
                    <cbc:ID schemeName="contract">CON-0001</cbc:ID>
                    <cac:SignatoryParty>
                        <cac:PartyIdentification>
                            <cbc:ID schemeName="organization">ORG-0001</cbc:ID>
                        </cac:PartyIdentification>
                    </cac:SignatoryParty>
                </efac:SettledContract>
            </efac:NoticeResult>
        </efext:EformsExtension>
    </root>
    """

    result = parse_signatory_identifier_reference(xml_content)

    assert result is not None
    assert "parties" in result
    assert "awards" in result
    assert len(result["parties"]) == 1
    assert len(result["awards"]) == 1

    party = result["parties"][0]
    assert party["id"] == "ORG-0001"
    assert party["name"] == "Financial Administration for ..."
    assert party["roles"] == ["buyer"]

    award = result["awards"][0]
    assert award["id"] == "CON-0001"
    assert award["buyers"][0]["id"] == "ORG-0001"


def test_merge_signatory_identifier_reference() -> None:
    release_json = {"parties": [], "awards": []}
    signatory_data = {
        "parties": [
            {
                "id": "ORG-0001",
                "name": "Financial Administration for ...",
                "roles": ["buyer"],
            }
        ],
        "awards": [{"id": "CON-0001", "buyers": [{"id": "ORG-0001"}]}],
    }

    merge_signatory_identifier_reference(release_json, signatory_data)

    assert "parties" in release_json
    assert "awards" in release_json
    assert len(release_json["parties"]) == 1
    assert len(release_json["awards"]) == 1

    party = release_json["parties"][0]
    assert party["id"] == "ORG-0001"
    assert party["name"] == "Financial Administration for ..."
    assert party["roles"] == ["buyer"]

    award = release_json["awards"][0]
    assert award["id"] == "CON-0001"
    assert award["buyers"][0]["id"] == "ORG-0001"


def test_merge_signatory_identifier_reference_existing_data() -> None:
    release_json = {
        "parties": [
            {"id": "ORG-0001", "name": "Existing Organization", "roles": ["supplier"]}
        ],
        "awards": [{"id": "CON-0001", "title": "Existing Award"}],
    }
    signatory_data = {
        "parties": [
            {
                "id": "ORG-0001",
                "name": "Financial Administration for ...",
                "roles": ["buyer"],
            }
        ],
        "awards": [{"id": "CON-0001", "buyers": [{"id": "ORG-0001"}]}],
    }

    merge_signatory_identifier_reference(release_json, signatory_data)

    assert len(release_json["parties"]) == 1
    assert len(release_json["awards"]) == 1

    party = release_json["parties"][0]
    assert party["id"] == "ORG-0001"
    assert party["name"] == "Existing Organization"
    assert set(party["roles"]) == {"supplier", "buyer"}

    award = release_json["awards"][0]
    assert award["id"] == "CON-0001"
    assert award["title"] == "Existing Award"
    assert award["buyers"][0]["id"] == "ORG-0001"
