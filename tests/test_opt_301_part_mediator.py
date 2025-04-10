# tests/test_opt_301_part_mediator.py

from src.ted_and_doffin_to_ocds.converters.eforms.opt_301_part_mediator import (
    merge_mediator_part,
    parse_mediator_part,
)


def test_parse_mediator() -> None:
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Part">1</cbc:ID>
            <cac:TenderingTerms>
                <cac:AppealTerms>
                    <cac:MediationParty>
                        <cac:PartyIdentification>
                            <cbc:ID schemeName="organization">ORG-0003</cbc:ID>
                        </cac:PartyIdentification>
                    </cac:MediationParty>
                </cac:AppealTerms>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </root>
    """
    result = parse_mediator_part(xml_content)
    assert result == {"parties": [{"id": "ORG-0003", "roles": ["mediationBody"]}]}


def test_merge_mediator() -> None:
    release_json = {"parties": [{"id": "ORG-0003", "roles": ["buyer"]}]}
    mediator_data = {"parties": [{"id": "ORG-0003", "roles": ["mediationBody"]}]}
    merge_mediator_part(release_json, mediator_data)
    assert release_json == {
        "parties": [{"id": "ORG-0003", "roles": ["buyer", "mediationBody"]}]
    }


def test_merge_mediator_new_party() -> None:
    release_json = {"parties": [{"id": "ORG-0001", "roles": ["buyer"]}]}
    mediator_data = {"parties": [{"id": "ORG-0003", "roles": ["mediationBody"]}]}
    merge_mediator_part(release_json, mediator_data)
    assert release_json == {
        "parties": [
            {"id": "ORG-0001", "roles": ["buyer"]},
            {"id": "ORG-0003", "roles": ["mediationBody"]},
        ]
    }


def test_merge_mediator_no_data() -> None:
    release_json = {"parties": [{"id": "ORG-0001", "roles": ["buyer"]}]}
    merge_mediator_part(release_json, None)
    assert release_json == {"parties": [{"id": "ORG-0001", "roles": ["buyer"]}]}
