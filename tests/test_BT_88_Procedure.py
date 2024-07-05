# tests/test_BT_88_Procedure.py

import pytest
from lxml import etree
from converters.BT_88_Procedure import parse_procedure_features, merge_procedure_features

def test_parse_procedure_features():
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:TenderingProcess>
            <cbc:Description>A two stage procedure ...</cbc:Description>
        </cac:TenderingProcess>
    </root>
    """
    
    result = parse_procedure_features(xml_content)
    assert result == {"tender": {"procurementMethodDetails": "A two stage procedure ..."}}

def test_merge_procedure_features():
    release_json = {}
    procedure_features_data = {"tender": {"procurementMethodDetails": "A two stage procedure ..."}}
    
    merge_procedure_features(release_json, procedure_features_data)
    assert release_json == {"tender": {"procurementMethodDetails": "A two stage procedure ..."}}

def test_merge_procedure_features_empty():
    release_json = {}
    procedure_features_data = None
    
    merge_procedure_features(release_json, procedure_features_data)
    assert release_json == {}