# tests/test_opt_301_part_tendereval.py

from src.ted_and_doffin_to_ocds.converters.eforms.opt_301_part_tendereval import (
    part_merge_tender_evaluator,
    part_parse_tender_evaluator,
)


def test_parse_tender_evaluator() -> None:
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Part">1</cbc:ID>
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
    result = part_parse_tender_evaluator(xml_content)
    assert result == {"parties": [{"id": "TPO-0001", "roles": ["evaluationBody"]}]}


def test_merge_tender_evaluator() -> None:
    release_json = {"parties": [{"id": "TPO-0001", "roles": ["buyer"]}]}
    tender_evaluator_data = {
        "parties": [{"id": "TPO-0001", "roles": ["evaluationBody"]}]
    }
    part_merge_tender_evaluator(release_json, tender_evaluator_data)
    assert release_json == {
        "parties": [{"id": "TPO-0001", "roles": ["buyer", "evaluationBody"]}]
    }


def test_merge_tender_evaluator_new_party() -> None:
    release_json = {"parties": [{"id": "ORG-0001", "roles": ["buyer"]}]}
    tender_evaluator_data = {
        "parties": [{"id": "TPO-0001", "roles": ["evaluationBody"]}]
    }
    part_merge_tender_evaluator(release_json, tender_evaluator_data)
    assert release_json == {
        "parties": [
            {"id": "ORG-0001", "roles": ["buyer"]},
            {"id": "TPO-0001", "roles": ["evaluationBody"]},
        ]
    }


def test_merge_tender_evaluator_no_data() -> None:
    release_json = {"parties": [{"id": "ORG-0001", "roles": ["buyer"]}]}
    part_merge_tender_evaluator(release_json, None)
    assert release_json == {"parties": [{"id": "ORG-0001", "roles": ["buyer"]}]}
