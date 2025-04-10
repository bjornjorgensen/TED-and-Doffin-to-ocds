# tests/test_opt_301_lot_reviewinfo.py

import pytest

from src.ted_and_doffin_to_ocds.converters.eforms.opt_301_lot_reviewinfo import (
    merge_review_info_provider_identifier,
    parse_review_info_provider_identifier,
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


def test_parse_review_info_provider_identifier(sample_xml) -> None:
    result = parse_review_info_provider_identifier(sample_xml)
    assert result is not None
    assert "parties" in result
    assert len(result["parties"]) == 1
    assert result["parties"][0]["id"] == "TPO-0001"
    assert result["parties"][0]["roles"] == ["reviewContactPoint"]


def test_merge_review_info_provider_identifier() -> None:
    review_info_data = {
        "parties": [{"id": "TPO-0001", "roles": ["reviewContactPoint"]}]
    }
    release_json = {}
    merge_review_info_provider_identifier(release_json, review_info_data)
    assert "parties" in release_json
    assert len(release_json["parties"]) == 1
    assert release_json["parties"][0]["id"] == "TPO-0001"
    assert release_json["parties"][0]["roles"] == ["reviewContactPoint"]


def test_merge_review_info_provider_identifier_existing_party() -> None:
    review_info_data = {
        "parties": [{"id": "TPO-0001", "roles": ["reviewContactPoint"]}]
    }
    release_json = {"parties": [{"id": "TPO-0001", "roles": ["buyer"]}]}
    merge_review_info_provider_identifier(release_json, review_info_data)
    assert len(release_json["parties"]) == 1
    assert release_json["parties"][0]["id"] == "TPO-0001"
    assert set(release_json["parties"][0]["roles"]) == {"buyer", "reviewContactPoint"}


def test_parse_review_info_provider_identifier_no_data() -> None:
    xml_content = "<root></root>"
    result = parse_review_info_provider_identifier(xml_content)
    assert result is None


def test_merge_review_info_provider_identifier_no_data() -> None:
    release_json = {}
    merge_review_info_provider_identifier(release_json, None)
    assert release_json == {}
