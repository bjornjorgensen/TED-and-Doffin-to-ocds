# tests/test_BT_04.py
from converters.BT_04 import parse_procedure_identifier

def test_parse_procedure_identifier():
    # Sample XML content for testing
    xml_content = """
    <root xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cbc:ContractFolderID>1e86a664-ae3c-41eb-8529-0242ac130003</cbc:ContractFolderID>
    </root>
    """
    
    # Expected output
    expected_output = {
        "tender": {
            "id": "1e86a664-ae3c-41eb-8529-0242ac130003"
        }
    }
    
    # Parse the XML content
    result = parse_procedure_identifier(xml_content)
    
    # Assert the result
    assert result == expected_output