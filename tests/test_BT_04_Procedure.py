# tests/test_BT_04_Procedure.py

import pytest
from lxml import etree
from converters.BT_04_Procedure import parse_procedure_identifier, merge_procedure_identifier

def test_parse_procedure_identifier():
    xml_content = """
    <root xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cbc:ContractFolderID>1e86a664-ae3c-41eb-8529-0242ac130003</cbc:ContractFolderID>
    </root>
    """
    result = parse_procedure_identifier(xml_content)
    assert result == {
        "tender": {
            "id": "1e86a664-ae3c-41eb-8529-0242ac130003"
        }
    }

def test_merge_procedure_identifier():
    release_json = {
        "tender": {
            "title": "Some tender title"
        }
    }
    procedure_identifier_data = {
        "tender": {
            "id": "1e86a664-ae3c-41eb-8529-0242ac130003"
        }
    }
    merge_procedure_identifier(release_json, procedure_identifier_data)
    assert release_json == {
        "tender": {
            "title": "Some tender title",
            "id": "1e86a664-ae3c-41eb-8529-0242ac130003"
        }
    }

def test_parse_procedure_identifier_not_found():
    xml_content = """
    <root xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cbc:SomeOtherElement>SomeValue</cbc:SomeOtherElement>
    </root>
    """
    result = parse_procedure_identifier(xml_content)
    assert result is None

def test_merge_procedure_identifier_empty_data():
    release_json = {
        "tender": {
            "title": "Some tender title"
        }
    }
    merge_procedure_identifier(release_json, None)
    assert release_json == {
        "tender": {
            "title": "Some tender title"
        }
    }