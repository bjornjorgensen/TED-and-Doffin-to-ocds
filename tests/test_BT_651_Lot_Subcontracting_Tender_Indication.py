# tests/test_BT_651_Lot_Subcontracting_Tender_Indication.py

import pytest
from lxml import etree
from converters.BT_651_Lot_Subcontracting_Tender_Indication import parse_subcontracting_tender_indication, merge_subcontracting_tender_indication

def test_parse_subcontracting_tender_indication():
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
          xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
          xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:TenderingTerms>
                <ext:UBLExtensions>
                    <ext:UBLExtension>
                        <ext:ExtensionContent>
                            <efext:EformsExtension>
                                <efac:TenderSubcontractingRequirements>
                                    <efbc:TenderSubcontractingRequirementsCode listName="subcontracting-indication">subc-oblig</efbc:TenderSubcontractingRequirementsCode>
                                </efac:TenderSubcontractingRequirements>
                            </efext:EformsExtension>
                        </ext:ExtensionContent>
                    </ext:UBLExtension>
                </ext:UBLExtensions>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </root>
    """.encode('utf-8')

    result = parse_subcontracting_tender_indication(xml_content)

    assert result is not None
    assert len(result['tender']['lots']) == 1
    lot = result['tender']['lots'][0]
    assert lot['id'] == 'LOT-0001'
    assert lot['submissionTerms']['subcontractingClauses'] == ['subc-oblig']

def test_parse_subcontracting_tender_indication_no_data():
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
        </cac:ProcurementProjectLot>
    </root>
    """.encode('utf-8')

    result = parse_subcontracting_tender_indication(xml_content)

    assert result is None

def test_merge_subcontracting_tender_indication():
    existing_release = {
        "tender": {
            "lots": [
                {
                    "id": "LOT-0001",
                    "submissionTerms": {
                        "subcontractingClauses": ["existing-clause"]
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
                    "submissionTerms": {
                        "subcontractingClauses": ["subc-oblig"]
                    }
                }
            ]
        }
    }

    merge_subcontracting_tender_indication(existing_release, new_data)

    assert len(existing_release['tender']['lots']) == 1
    lot = existing_release['tender']['lots'][0]
    assert lot['submissionTerms']['subcontractingClauses'] == ["existing-clause", "subc-oblig"]

def test_merge_subcontracting_tender_indication_new_lot():
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
                    "submissionTerms": {
                        "subcontractingClauses": ["subc-oblig"]
                    }
                }
            ]
        }
    }

    merge_subcontracting_tender_indication(existing_release, new_data)

    assert len(existing_release['tender']['lots']) == 1
    lot = existing_release['tender']['lots'][0]
    assert lot['id'] == 'LOT-0001'
    assert lot['submissionTerms']['subcontractingClauses'] == ["subc-oblig"]