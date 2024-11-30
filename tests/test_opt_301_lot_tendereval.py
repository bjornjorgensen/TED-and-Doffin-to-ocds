# tests/test_opt_301_lot_tendereval.py

from ted_and_doffin_to_ocds.converters.opt_301_lot_tendereval import (
    merge_tender_evaluator,
    parse_tender_evaluator,
)


def test_parse_tender_evaluator() -> None:
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:TenderingTerms>
                <cac:TenderEvaluationParty>
                    <cac:PartyIdentification>
                        <cbc:ID schemeName="touchpoint">TPO-0001</cbc:ID>
                    </cac:PartyIdentification>
                </cac:TenderEvaluationParty>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </root>
    """

    result = parse_tender_evaluator(xml_content)

    assert result is not None
    assert "parties" in result
    assert len(result["parties"]) == 1

    party = result["parties"][0]
    assert party["id"] == "TPO-0001"
    assert party["roles"] == ["evaluationBody"]


def test_merge_tender_evaluator() -> None:
    release_json = {"parties": []}
    tender_evaluator_data = {
        "parties": [{"id": "TPO-0001", "roles": ["evaluationBody"]}]
    }

    merge_tender_evaluator(release_json, tender_evaluator_data)

    assert "parties" in release_json
    assert len(release_json["parties"]) == 1

    party = release_json["parties"][0]
    assert party["id"] == "TPO-0001"
    assert party["roles"] == ["evaluationBody"]


def test_merge_tender_evaluator_existing_party() -> None:
    release_json = {
        "parties": [
            {"id": "TPO-0001", "name": "Existing Organization", "roles": ["buyer"]}
        ]
    }
    tender_evaluator_data = {
        "parties": [{"id": "TPO-0001", "roles": ["evaluationBody"]}]
    }

    merge_tender_evaluator(release_json, tender_evaluator_data)

    assert len(release_json["parties"]) == 1

    party = release_json["parties"][0]
    assert party["id"] == "TPO-0001"
    assert party["name"] == "Existing Organization"
    assert set(party["roles"]) == {"buyer", "evaluationBody"}
