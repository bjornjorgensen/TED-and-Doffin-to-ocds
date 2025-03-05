# tests/test_opt_301_part_revieworg.py

from src.ted_and_doffin_to_ocds.converters.eforms.opt_301_part_revieworg import (
    merge_review_organization_part,
    parse_review_organization_part,
)


def test_parse_review_organization() -> None:
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Part">1</cbc:ID>
            <cac:TenderingTerms>
                <cac:AppealTerms>
                    <cac:AppealReceiverParty>
                        <cac:PartyIdentification>
                            <cbc:ID schemeName="touchpoint">TPO-0003</cbc:ID>
                        </cac:PartyIdentification>
                    </cac:AppealReceiverParty>
                </cac:AppealTerms>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </root>
    """
    result = parse_review_organization_part(xml_content)
    assert result == {"parties": [{"id": "TPO-0003", "roles": ["reviewBody"]}]}


def test_merge_review_organization() -> None:
    release_json = {"parties": [{"id": "TPO-0003", "roles": ["buyer"]}]}
    review_organization_data = {
        "parties": [{"id": "TPO-0003", "roles": ["reviewBody"]}]
    }
    merge_review_organization_part(release_json, review_organization_data)
    assert release_json == {
        "parties": [{"id": "TPO-0003", "roles": ["buyer", "reviewBody"]}]
    }


def test_merge_review_organization_new_party() -> None:
    release_json = {"parties": [{"id": "ORG-0001", "roles": ["buyer"]}]}
    review_organization_data = {
        "parties": [{"id": "TPO-0003", "roles": ["reviewBody"]}]
    }
    merge_review_organization_part(release_json, review_organization_data)
    assert release_json == {
        "parties": [
            {"id": "ORG-0001", "roles": ["buyer"]},
            {"id": "TPO-0003", "roles": ["reviewBody"]},
        ]
    }


def test_merge_review_organization_no_data() -> None:
    release_json = {"parties": [{"id": "ORG-0001", "roles": ["buyer"]}]}
    merge_review_organization_part(release_json, None)
    assert release_json == {"parties": [{"id": "ORG-0001", "roles": ["buyer"]}]}
