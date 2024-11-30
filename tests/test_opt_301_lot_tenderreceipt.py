# tests/test_opt_301_lot_tenderreceipt.py

from ted_and_doffin_to_ocds.converters.opt_301_lot_tenderreceipt import (
    merge_tender_recipient,
    parse_tender_recipient,
)


def test_parse_tender_recipient() -> None:
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
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

    result = parse_tender_recipient(xml_content)

    assert result is not None
    assert "parties" in result
    assert len(result["parties"]) == 1

    party = result["parties"][0]
    assert party["id"] == "TPO-0001"
    assert party["roles"] == ["submissionReceiptBody"]


def test_merge_tender_recipient() -> None:
    release_json = {"parties": []}
    tender_recipient_data = {
        "parties": [{"id": "TPO-0001", "roles": ["submissionReceiptBody"]}]
    }

    merge_tender_recipient(release_json, tender_recipient_data)

    assert "parties" in release_json
    assert len(release_json["parties"]) == 1

    party = release_json["parties"][0]
    assert party["id"] == "TPO-0001"
    assert party["roles"] == ["submissionReceiptBody"]


def test_merge_tender_recipient_existing_party() -> None:
    release_json = {
        "parties": [
            {"id": "TPO-0001", "name": "Existing Organization", "roles": ["buyer"]}
        ]
    }
    tender_recipient_data = {
        "parties": [{"id": "TPO-0001", "roles": ["submissionReceiptBody"]}]
    }

    merge_tender_recipient(release_json, tender_recipient_data)

    assert len(release_json["parties"]) == 1

    party = release_json["parties"][0]
    assert party["id"] == "TPO-0001"
    assert party["name"] == "Existing Organization"
    assert set(party["roles"]) == {"buyer", "submissionReceiptBody"}
