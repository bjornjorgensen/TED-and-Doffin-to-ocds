# tests/test_opt_301_lot_addinfo.py

from src.ted_and_doffin_to_ocds.converters.eforms.opt_301_lot_addinfo import (
    merge_additional_info_provider,
    parse_additional_info_provider,
)


def test_parse_additional_info_provider() -> None:
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-001</cbc:ID>
            <cac:TenderingTerms>
                <cac:AdditionalInformationParty>
                    <cac:PartyIdentification>
                        <cbc:ID schemeName="touchpoint">TPO-0001</cbc:ID>
                    </cac:PartyIdentification>
                </cac:AdditionalInformationParty>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </root>
    """

    result = parse_additional_info_provider(xml_content)

    assert result is not None
    assert "parties" in result
    assert len(result["parties"]) == 1

    party = result["parties"][0]
    assert party["id"] == "TPO-0001"
    assert party["roles"] == ["processContactPoint"]


def test_merge_additional_info_provider() -> None:
    release_json = {"parties": []}
    provider_data = {"parties": [{"id": "TPO-0001", "roles": ["processContactPoint"]}]}

    merge_additional_info_provider(release_json, provider_data)

    assert "parties" in release_json
    assert len(release_json["parties"]) == 1

    party = release_json["parties"][0]
    assert party["id"] == "TPO-0001"
    assert party["roles"] == ["processContactPoint"]


def test_merge_additional_info_provider_existing_party() -> None:
    release_json = {
        "parties": [
            {"id": "TPO-0001", "name": "Existing Organization", "roles": ["buyer"]}
        ]
    }
    provider_data = {"parties": [{"id": "TPO-0001", "roles": ["processContactPoint"]}]}

    merge_additional_info_provider(release_json, provider_data)

    assert len(release_json["parties"]) == 1

    party = release_json["parties"][0]
    assert party["id"] == "TPO-0001"
    assert party["name"] == "Existing Organization"
    assert set(party["roles"]) == {"buyer", "processContactPoint"}
