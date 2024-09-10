# tests/test_OPT_301_Lot_Mediator.py

from ted_and_doffin_to_ocds.converters.OPT_301_Lot_Mediator import (
    parse_mediator_identifier,
    merge_mediator_identifier,
)


def test_parse_mediator_identifier():
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">1</cbc:ID>
            <cac:TenderingTerms>
                <cac:AppealTerms>
                    <cac:MediationParty>
                        <cac:PartyIdentification>
                            <cbc:ID>TPO-0005</cbc:ID>
                        </cac:PartyIdentification>
                    </cac:MediationParty>
                </cac:AppealTerms>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </root>
    """

    result = parse_mediator_identifier(xml_content)

    assert result is not None
    assert "parties" in result
    assert len(result["parties"]) == 1
    assert result["parties"][0]["id"] == "TPO-0005"
    assert result["parties"][0]["roles"] == ["mediationBody"]


def test_parse_mediator_identifier_no_data():
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">1</cbc:ID>
        </cac:ProcurementProjectLot>
    </root>
    """

    result = parse_mediator_identifier(xml_content)

    assert result is None


def test_merge_mediator_identifier():
    mediator_data = {"parties": [{"id": "TPO-0005", "roles": ["mediationBody"]}]}

    release_json = {
        "parties": [{"id": "TPO-0001", "name": "Existing Party", "roles": ["buyer"]}]
    }

    merge_mediator_identifier(release_json, mediator_data)

    assert len(release_json["parties"]) == 2
    assert release_json["parties"][0]["id"] == "TPO-0001"
    assert release_json["parties"][0]["roles"] == ["buyer"]
    assert release_json["parties"][1]["id"] == "TPO-0005"
    assert release_json["parties"][1]["roles"] == ["mediationBody"]


def test_merge_mediator_identifier_existing_party():
    mediator_data = {"parties": [{"id": "TPO-0001", "roles": ["mediationBody"]}]}

    release_json = {
        "parties": [{"id": "TPO-0001", "name": "Existing Party", "roles": ["buyer"]}]
    }

    merge_mediator_identifier(release_json, mediator_data)

    assert len(release_json["parties"]) == 1
    assert release_json["parties"][0]["id"] == "TPO-0001"
    assert set(release_json["parties"][0]["roles"]) == {"buyer", "mediationBody"}
    assert release_json["parties"][0]["name"] == "Existing Party"


def test_merge_mediator_identifier_no_data():
    release_json = {"parties": []}
    merge_mediator_identifier(release_json, None)
    assert release_json == {"parties": []}
