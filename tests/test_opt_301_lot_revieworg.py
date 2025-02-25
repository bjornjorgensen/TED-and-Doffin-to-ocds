# tests/test_opt_301_lot_revieworg.py

import pytest

from src.ted_and_doffin_to_ocds.converters.eforms.opt_301_lot_revieworg import (
    merge_review_organization_identifier,
    parse_review_organization_identifier,
)


@pytest.fixture
def sample_xml() -> str:
    return """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
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


def test_parse_review_organization_identifier(sample_xml) -> None:
    result = parse_review_organization_identifier(sample_xml)
    assert result is not None
    assert "parties" in result
    assert len(result["parties"]) == 1
    assert result["parties"][0]["id"] == "TPO-0003"
    assert result["parties"][0]["roles"] == ["reviewBody"]


def test_merge_review_organization_identifier() -> None:
    review_org_data = {"parties": [{"id": "TPO-0003", "roles": ["reviewBody"]}]}
    release_json = {}
    merge_review_organization_identifier(release_json, review_org_data)
    assert "parties" in release_json
    assert len(release_json["parties"]) == 1
    assert release_json["parties"][0]["id"] == "TPO-0003"
    assert release_json["parties"][0]["roles"] == ["reviewBody"]


def test_merge_review_organization_identifier_existing_party() -> None:
    review_org_data = {"parties": [{"id": "TPO-0003", "roles": ["reviewBody"]}]}
    release_json = {"parties": [{"id": "TPO-0003", "roles": ["buyer"]}]}
    merge_review_organization_identifier(release_json, review_org_data)
    assert len(release_json["parties"]) == 1
    assert release_json["parties"][0]["id"] == "TPO-0003"
    assert set(release_json["parties"][0]["roles"]) == {"buyer", "reviewBody"}


def test_parse_review_organization_identifier_no_data() -> None:
    xml_content = "<root></root>"
    result = parse_review_organization_identifier(xml_content)
    assert result is None


def test_merge_review_organization_identifier_no_data() -> None:
    release_json = {}
    merge_review_organization_identifier(release_json, None)
    assert release_json == {}
