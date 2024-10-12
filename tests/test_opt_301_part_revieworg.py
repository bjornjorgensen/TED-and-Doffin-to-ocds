# tests/test_opt_301_part_revieworg.py

from ted_and_doffin_to_ocds.converters.opt_301_part_revieworg import (
    part_parse_review_organization,
    part_merge_review_organization,
)


def test_parse_review_organization():
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
    result = part_parse_review_organization(xml_content)
    assert result == {"parties": [{"id": "TPO-0003", "roles": ["reviewBody"]}]}


def test_merge_review_organization():
    release_json = {"parties": [{"id": "TPO-0003", "roles": ["buyer"]}]}
    review_organization_data = {
        "parties": [{"id": "TPO-0003", "roles": ["reviewBody"]}]
    }
    part_merge_review_organization(release_json, review_organization_data)
    assert release_json == {
        "parties": [{"id": "TPO-0003", "roles": ["buyer", "reviewBody"]}]
    }


def test_merge_review_organization_new_party():
    release_json = {"parties": [{"id": "ORG-0001", "roles": ["buyer"]}]}
    review_organization_data = {
        "parties": [{"id": "TPO-0003", "roles": ["reviewBody"]}]
    }
    part_merge_review_organization(release_json, review_organization_data)
    assert release_json == {
        "parties": [
            {"id": "ORG-0001", "roles": ["buyer"]},
            {"id": "TPO-0003", "roles": ["reviewBody"]},
        ]
    }


def test_merge_review_organization_no_data():
    release_json = {"parties": [{"id": "ORG-0001", "roles": ["buyer"]}]}
    part_merge_review_organization(release_json, None)
    assert release_json == {"parties": [{"id": "ORG-0001", "roles": ["buyer"]}]}
