# tests/test_BT_65_Lot_Subcontracting_Obligation.py

import pytest
from lxml import etree
from converters.BT_65_Lot_Subcontracting_Obligation import parse_subcontracting_obligation, merge_subcontracting_obligation, SUBCONTRACTING_OBLIGATION_MAPPING

def test_parse_subcontracting_obligation():
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:TenderingTerms>
                <cac:AllowedSubcontractTerms>
                    <cbc:SubcontractingConditionsCode listName="subcontracting-obligation">subc-min</cbc:SubcontractingConditionsCode>
                </cac:AllowedSubcontractTerms>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </root>
    """.encode('utf-8')

    result = parse_subcontracting_obligation(xml_content)

    assert result is not None
    assert len(result['tender']['lots']) == 1
    lot = result['tender']['lots'][0]
    assert lot['id'] == 'LOT-0001'
    assert lot['subcontractingTerms']['description'] == SUBCONTRACTING_OBLIGATION_MAPPING['subc-min']

def test_parse_subcontracting_obligation_none():
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:TenderingTerms>
                <cac:AllowedSubcontractTerms>
                    <cbc:SubcontractingConditionsCode listName="subcontracting-obligation">none</cbc:SubcontractingConditionsCode>
                </cac:AllowedSubcontractTerms>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </root>
    """.encode('utf-8')

    result = parse_subcontracting_obligation(xml_content)

    assert result is None

def test_parse_subcontracting_obligation_no_data():
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
        </cac:ProcurementProjectLot>
    </root>
    """.encode('utf-8')

    result = parse_subcontracting_obligation(xml_content)

    assert result is None

def test_merge_subcontracting_obligation():
    existing_release = {
        "tender": {
            "lots": [
                {
                    "id": "LOT-0001",
                    "subcontractingTerms": {
                        "description": "Old description"
                    }
                }
            ]
        }
    }

    new_data = {
        "tender": {
            "lots": [
                {
                    "id": "LOT-0001",
                    "subcontractingTerms": {
                        "description": "New description"
                    }
                }
            ]
        }
    }

    merge_subcontracting_obligation(existing_release, new_data)

    assert len(existing_release['tender']['lots']) == 1
    lot = existing_release['tender']['lots'][0]
    assert lot['subcontractingTerms']['description'] == "New description"

def test_merge_subcontracting_obligation_new_lot():
    existing_release = {
        "tender": {
            "lots": []
        }
    }

    new_data = {
        "tender": {
            "lots": [
                {
                    "id": "LOT-0001",
                    "subcontractingTerms": {
                        "description": "New description"
                    }
                }
            ]
        }
    }

    merge_subcontracting_obligation(existing_release, new_data)

    assert len(existing_release['tender']['lots']) == 1
    lot = existing_release['tender']['lots'][0]
    assert lot['id'] == 'LOT-0001'
    assert lot['subcontractingTerms']['description'] == "New description"