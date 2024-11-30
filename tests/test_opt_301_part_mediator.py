# tests/test_opt_301_part_mediator.py

from ted_and_doffin_to_ocds.converters.opt_301_part_mediator import (
    part_merge_mediator,
    part_parse_mediator,
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
    result = part_parse_mediator(xml_content)
    assert result == {"parties": [{"id": "ORG-0003", "roles": ["mediationBody"]}]}


def test_merge_mediator() -> None:
    release_json = {"parties": [{"id": "ORG-0003", "roles": ["buyer"]}]}
    mediator_data = {"parties": [{"id": "ORG-0003", "roles": ["mediationBody"]}]}
    part_merge_mediator(release_json, mediator_data)
    assert release_json == {
        "parties": [{"id": "ORG-0003", "roles": ["buyer", "mediationBody"]}]
    }


def test_merge_mediator_new_party() -> None:
    release_json = {"parties": [{"id": "ORG-0001", "roles": ["buyer"]}]}
    mediator_data = {"parties": [{"id": "ORG-0003", "roles": ["mediationBody"]}]}
    part_merge_mediator(release_json, mediator_data)
    assert release_json == {
        "parties": [
            {"id": "ORG-0001", "roles": ["buyer"]},
            {"id": "ORG-0003", "roles": ["mediationBody"]},
        ]
    }


def test_merge_mediator_no_data() -> None:
    release_json = {"parties": [{"id": "ORG-0001", "roles": ["buyer"]}]}
    part_merge_mediator(release_json, None)
    assert release_json == {"parties": [{"id": "ORG-0001", "roles": ["buyer"]}]}
