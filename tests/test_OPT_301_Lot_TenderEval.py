# tests/test_OPT_301_Lot_TenderEval.py

import pytest
from lxml import etree
from converters.OPT_301_Lot_TenderEval import parse_tender_evaluator_identifier, merge_tender_evaluator_identifier

def test_parse_tender_evaluator_identifier():
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">1</cbc:ID>
            <cac:TenderingTerms>
                <cac:TenderEvaluationParty>
                    <cac:PartyIdentification>
                        <cbc:ID>TPO-0001</cbc:ID>
                    </cac:PartyIdentification>
                </cac:TenderEvaluationParty>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </root>
    """

    result = parse_tender_evaluator_identifier(xml_content)

    assert result is not None
    assert "parties" in result
    assert len(result["parties"]) == 1
    assert result["parties"][0]["id"] == "TPO-0001"
    assert result["parties"][0]["roles"] == ["evaluationBody"]

def test_parse_tender_evaluator_identifier_no_data():
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">1</cbc:ID>
        </cac:ProcurementProjectLot>
    </root>
    """

    result = parse_tender_evaluator_identifier(xml_content)

    assert result is None

def test_merge_tender_evaluator_identifier():
    evaluator_data = {
        "parties": [
            {"id": "TPO-0001", "roles": ["evaluationBody"]}
        ]
    }

    release_json = {
        "parties": [
            {"id": "TPO-0002", "name": "Existing Party", "roles": ["buyer"]}
        ]
    }

    merge_tender_evaluator_identifier(release_json, evaluator_data)

    assert len(release_json["parties"]) == 2
    assert release_json["parties"][0]["id"] == "TPO-0002"
    assert release_json["parties"][0]["roles"] == ["buyer"]
    assert release_json["parties"][1]["id"] == "TPO-0001"
    assert release_json["parties"][1]["roles"] == ["evaluationBody"]

def test_merge_tender_evaluator_identifier_existing_party():
    evaluator_data = {
        "parties": [
            {"id": "TPO-0001", "roles": ["evaluationBody"]}
        ]
    }

    release_json = {
        "parties": [
            {"id": "TPO-0001", "name": "Existing Party", "roles": ["buyer"]}
        ]
    }

    merge_tender_evaluator_identifier(release_json, evaluator_data)

    assert len(release_json["parties"]) == 1
    assert release_json["parties"][0]["id"] == "TPO-0001"
    assert set(release_json["parties"][0]["roles"]) == set(["buyer", "evaluationBody"])
    assert release_json["parties"][0]["name"] == "Existing Party"

def test_merge_tender_evaluator_identifier_no_data():
    release_json = {"parties": []}
    merge_tender_evaluator_identifier(release_json, None)
    assert release_json == {"parties": []}