# tests/test_OPT_301_Lot_ReviewOrg.py

import pytest
from converters.OPT_301_Lot_ReviewOrg import (
    parse_review_org_identifier,
    merge_review_org_identifier,
)


def test_parse_review_org_identifier():
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">1</cbc:ID>
            <cac:TenderingTerms>
                <cac:AppealTerms>
                    <cac:AppealReceiverParty>
                        <cac:PartyIdentification>
                            <cbc:ID>TPO-0001</cbc:ID>
                        </cac:PartyIdentification>
                    </cac:AppealReceiverParty>
                </cac:AppealTerms>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">2</cbc:ID>
            <cac:TenderingTerms>
                <cac:AppealTerms>
                    <cac:AppealReceiverParty>
                        <cac:PartyIdentification>
                            <cbc:ID>TPO-0002</cbc:ID>
                        </cac:PartyIdentification>
                    </cac:AppealReceiverParty>
                </cac:AppealTerms>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </root>
    """

    result = parse_review_org_identifier(xml_content)

    assert result is not None
    assert "parties" in result
    assert len(result["parties"]) == 2
    assert result["parties"][0]["id"] == "TPO-0001"
    assert result["parties"][0]["roles"] == ["reviewBody"]
    assert result["parties"][1]["id"] == "TPO-0002"
    assert result["parties"][1]["roles"] == ["reviewBody"]


def test_parse_review_org_identifier_no_data():
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">1</cbc:ID>
        </cac:ProcurementProjectLot>
    </root>
    """

    result = parse_review_org_identifier(xml_content)

    assert result is None


def test_merge_review_org_identifier():
    review_org_data = {
        "parties": [
            {"id": "TPO-0001", "roles": ["reviewBody"]},
            {"id": "TPO-0002", "roles": ["reviewBody"]},
        ]
    }

    release_json = {
        "parties": [{"id": "TPO-0001", "name": "Existing Party", "roles": ["buyer"]}]
    }

    merge_review_org_identifier(release_json, review_org_data)

    assert len(release_json["parties"]) == 2
    assert release_json["parties"][0]["id"] == "TPO-0001"
    assert set(release_json["parties"][0]["roles"]) == {"buyer", "reviewBody"}
    assert release_json["parties"][1]["id"] == "TPO-0002"
    assert release_json["parties"][1]["roles"] == ["reviewBody"]


def test_merge_review_org_identifier_no_data():
    release_json = {"parties": []}
    merge_review_org_identifier(release_json, None)
    assert release_json == {"parties": []}


@pytest.fixture
def sample_release_json():
    return {
        "parties": [{"id": "TPO-0001", "name": "Existing Party", "roles": ["buyer"]}]
    }


def test_merge_review_org_identifier_existing_party(sample_release_json):
    review_org_data = {"parties": [{"id": "TPO-0001", "roles": ["reviewBody"]}]}

    merge_review_org_identifier(sample_release_json, review_org_data)

    assert len(sample_release_json["parties"]) == 1
    assert sample_release_json["parties"][0]["id"] == "TPO-0001"
    assert set(sample_release_json["parties"][0]["roles"]) == {"buyer", "reviewBody"}
    assert sample_release_json["parties"][0]["name"] == "Existing Party"


def test_merge_review_org_identifier_new_party(sample_release_json):
    review_org_data = {"parties": [{"id": "TPO-0002", "roles": ["reviewBody"]}]}

    merge_review_org_identifier(sample_release_json, review_org_data)

    assert len(sample_release_json["parties"]) == 2
    assert sample_release_json["parties"][1]["id"] == "TPO-0002"
    assert sample_release_json["parties"][1]["roles"] == ["reviewBody"]
