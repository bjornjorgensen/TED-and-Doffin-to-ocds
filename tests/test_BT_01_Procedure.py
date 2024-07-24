# tests/test_BT_01_Procedure.py

import pytest
from lxml import etree
from converters.BT_01_Procedure import (
    parse_procedure_legal_basis_id,
    parse_procedure_legal_basis_description,
    parse_procedure_legal_basis_noid,
    parse_procedure_legal_basis_noid_description,
    parse_procedure_legal_basis_notice,
    merge_procedure_legal_basis
)

def test_parse_procedure_legal_basis_id():
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:TenderingTerms>
            <cac:ProcurementLegislationDocumentReference>
                <cbc:ID>http://data.europa.eu/eli/dir/2014/24/oj</cbc:ID>
            </cac:ProcurementLegislationDocumentReference>
        </cac:TenderingTerms>
    </root>
    """
    result = parse_procedure_legal_basis_id(xml_content)
    assert result == {
        "tender": {
            "legalBasis": {
                "scheme": "ELI",
                "id": "http://data.europa.eu/eli/dir/2014/24/oj"
            }
        }
    }

def test_parse_procedure_legal_basis_description():
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:TenderingTerms>
            <cac:ProcurementLegislationDocumentReference>
                <cbc:DocumentDescription>Directive XYZ applies ...</cbc:DocumentDescription>
            </cac:ProcurementLegislationDocumentReference>
        </cac:TenderingTerms>
    </root>
    """
    result = parse_procedure_legal_basis_description(xml_content)
    assert result == {
        "tender": {
            "legalBasis": {
                "description": "Directive XYZ applies ..."
            }
        }
    }

def test_parse_procedure_legal_basis_noid():
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:TenderingTerms>
            <cac:ProcurementLegislationDocumentReference>
                <cbc:ID>LocalLegalBasis</cbc:ID>
            </cac:ProcurementLegislationDocumentReference>
        </cac:TenderingTerms>
    </root>
    """
    result = parse_procedure_legal_basis_noid(xml_content)
    assert result == {
        "tender": {
            "legalBasis": {
                "id": "LocalLegalBasis"
            }
        }
    }

def test_parse_procedure_legal_basis_noid_description():
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:TenderingTerms>
            <cac:ProcurementLegislationDocumentReference>
                <cbc:ID>LocalLegalBasis</cbc:ID>
                <cbc:DocumentDescription>Local legal basis description</cbc:DocumentDescription>
            </cac:ProcurementLegislationDocumentReference>
        </cac:TenderingTerms>
    </root>
    """
    result = parse_procedure_legal_basis_noid_description(xml_content)
    assert result == {
        "tender": {
            "legalBasis": {
                "description": "Local legal basis description"
            }
        }
    }

def test_parse_procedure_legal_basis_notice():
    xml_content = """
    <root xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cbc:RegulatoryDomain>32014L0024</cbc:RegulatoryDomain>
    </root>
    """
    result = parse_procedure_legal_basis_notice(xml_content)
    assert result == {
        "tender": {
            "legalBasis": {
                "scheme": "CELEX",
                "id": "32014L0024"
            }
        }
    }

def test_merge_procedure_legal_basis():
    release_json = {
        "tender": {
            "legalBasis": {
                "id": "existing-id"
            }
        }
    }
    legal_basis_data = {
        "tender": {
            "legalBasis": {
                "scheme": "CELEX",
                "id": "32014L0024",
                "description": "New description"
            }
        }
    }
    merge_procedure_legal_basis(release_json, legal_basis_data)
    assert release_json == {
        "tender": {
            "legalBasis": {
                "scheme": "CELEX",
                "id": "32014L0024",
                "description": "New description"
            }
        }
    }

def test_parse_functions_not_found():
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:SomeOtherElement>
            <cbc:SomeOtherID>SomeValue</cbc:SomeOtherID>
        </cac:SomeOtherElement>
    </root>
    """
    assert parse_procedure_legal_basis_id(xml_content) is None
    assert parse_procedure_legal_basis_description(xml_content) is None
    assert parse_procedure_legal_basis_noid(xml_content) is None
    assert parse_procedure_legal_basis_noid_description(xml_content) is None
    assert parse_procedure_legal_basis_notice(xml_content) is None