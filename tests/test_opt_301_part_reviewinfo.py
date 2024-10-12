# tests/test_opt_301_part_reviewinfo.py

from ted_and_doffin_to_ocds.converters.opt_301_part_reviewinfo import (
    part_parse_review_info_provider,
    part_merge_review_info_provider,
)


def test_parse_review_info_provider():
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Part">1</cbc:ID>
            <cac:TenderingTerms>
                <cac:AppealTerms>
                    <cac:AppealInformationParty>
                        <cac:PartyIdentification>
                            <cbc:ID schemeName="touchpoint">TPO-0001</cbc:ID>
                        </cac:PartyIdentification>
                    </cac:AppealInformationParty>
                </cac:AppealTerms>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </root>
    """
    result = part_parse_review_info_provider(xml_content)
    assert result == {"parties": [{"id": "TPO-0001", "roles": ["reviewContactPoint"]}]}


def test_merge_review_info_provider():
    release_json = {"parties": [{"id": "TPO-0001", "roles": ["buyer"]}]}
    review_info_provider_data = {
        "parties": [{"id": "TPO-0001", "roles": ["reviewContactPoint"]}]
    }
    part_merge_review_info_provider(release_json, review_info_provider_data)
    assert release_json == {
        "parties": [{"id": "TPO-0001", "roles": ["buyer", "reviewContactPoint"]}]
    }


def test_merge_review_info_provider_new_party():
    release_json = {"parties": [{"id": "ORG-0001", "roles": ["buyer"]}]}
    review_info_provider_data = {
        "parties": [{"id": "TPO-0001", "roles": ["reviewContactPoint"]}]
    }
    part_merge_review_info_provider(release_json, review_info_provider_data)
    assert release_json == {
        "parties": [
            {"id": "ORG-0001", "roles": ["buyer"]},
            {"id": "TPO-0001", "roles": ["reviewContactPoint"]},
        ]
    }


def test_merge_review_info_provider_no_data():
    release_json = {"parties": [{"id": "ORG-0001", "roles": ["buyer"]}]}
    part_merge_review_info_provider(release_json, None)
    assert release_json == {"parties": [{"id": "ORG-0001", "roles": ["buyer"]}]}
