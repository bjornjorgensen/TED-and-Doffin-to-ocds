# tests/test_opt_301_part_tenderreceipt.py

from src.ted_and_doffin_to_ocds.converters.eforms.opt_301_part_tenderreceipt import (
    merge_tender_recipient_part,
    parse_tender_recipient_part,
)


def test_parse_tender_recipient() -> None:
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Part">1</cbc:ID>
            <cac:TenderingTerms>
                <cac:TenderRecipientParty>
                    <cac:PartyIdentification>
                        <cbc:ID schemeName="touchpoint">TPO-0001</cbc:ID>
                    </cac:PartyIdentification>
                </cac:TenderRecipientParty>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </root>
    """
    result = part_parse_tender_recipient(xml_content)
    assert result == {
        "parties": [{"id": "TPO-0001", "roles": ["submissionReceiptBody"]}]
    }


def test_merge_tender_recipient() -> None:
    release_json = {"parties": [{"id": "TPO-0001", "roles": ["buyer"]}]}
    tender_recipient_data = {
        "parties": [{"id": "TPO-0001", "roles": ["submissionReceiptBody"]}]
    }
    part_merge_tender_recipient(release_json, tender_recipient_data)
    assert release_json == {
        "parties": [{"id": "TPO-0001", "roles": ["buyer", "submissionReceiptBody"]}]
    }


def test_merge_tender_recipient_new_party() -> None:
    release_json = {"parties": [{"id": "ORG-0001", "roles": ["buyer"]}]}
    tender_recipient_data = {
        "parties": [{"id": "TPO-0001", "roles": ["submissionReceiptBody"]}]
    }
    part_merge_tender_recipient(release_json, tender_recipient_data)
    assert release_json == {
        "parties": [
            {"id": "ORG-0001", "roles": ["buyer"]},
            {"id": "TPO-0001", "roles": ["submissionReceiptBody"]},
        ]
    }


def test_merge_tender_recipient_no_data() -> None:
    release_json = {"parties": [{"id": "ORG-0001", "roles": ["buyer"]}]}
    part_merge_tender_recipient(release_json, None)
    assert release_json == {"parties": [{"id": "ORG-0001", "roles": ["buyer"]}]}
