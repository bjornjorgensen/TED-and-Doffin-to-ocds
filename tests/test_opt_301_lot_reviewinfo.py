# tests/test_OPT_301_Lot_ReviewInfo.py

from ted_and_doffin_to_ocds.converters.opt_301_lot_reviewinfo import (
    parse_review_info_identifier,
    merge_review_info_identifier,
)


def test_parse_review_info_identifier():
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">1</cbc:ID>
            <cac:TenderingTerms>
                <cac:AppealTerms>
                    <cac:AppealInformationparty>
                        <cac:partyIdentification>
                            <cbc:ID>TPO-0001</cbc:ID>
                        </cac:partyIdentification>
                    </cac:AppealInformationparty>
                </cac:AppealTerms>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </root>
    """

    result = parse_review_info_identifier(xml_content)

    assert result is not None
    assert "parties" in result
    assert len(result["parties"]) == 1
    assert result["parties"][0]["id"] == "TPO-0001"
    assert result["parties"][0]["roles"] == ["reviewContactPoint"]


def test_parse_review_info_identifier_no_data():
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">1</cbc:ID>
        </cac:ProcurementProjectLot>
    </root>
    """

    result = parse_review_info_identifier(xml_content)

    assert result is None


def test_merge_review_info_identifier():
    review_info_data = {
        "parties": [{"id": "TPO-0001", "roles": ["reviewContactPoint"]}],
    }

    release_json = {
        "parties": [{"id": "TPO-0002", "name": "Existing party", "roles": ["buyer"]}],
    }

    merge_review_info_identifier(release_json, review_info_data)

    assert len(release_json["parties"]) == 2
    assert release_json["parties"][0]["id"] == "TPO-0002"
    assert release_json["parties"][0]["roles"] == ["buyer"]
    assert release_json["parties"][1]["id"] == "TPO-0001"
    assert release_json["parties"][1]["roles"] == ["reviewContactPoint"]


def test_merge_review_info_identifier_existing_party():
    review_info_data = {
        "parties": [{"id": "TPO-0001", "roles": ["reviewContactPoint"]}],
    }

    release_json = {
        "parties": [{"id": "TPO-0001", "name": "Existing party", "roles": ["buyer"]}],
    }

    merge_review_info_identifier(release_json, review_info_data)

    assert len(release_json["parties"]) == 1
    assert release_json["parties"][0]["id"] == "TPO-0001"
    assert set(release_json["parties"][0]["roles"]) == {"buyer", "reviewContactPoint"}
    assert release_json["parties"][0]["name"] == "Existing party"


def test_merge_review_info_identifier_no_data():
    release_json = {"parties": []}
    merge_review_info_identifier(release_json, None)
    assert release_json == {"parties": []}