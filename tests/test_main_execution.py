# test_main.py
import json
from main import main

def test_main_with_valid_xml():
    # Path to a valid XML file for testing
    xml_path = 'input_files/valid_xml.xml'
    ocid_prefix = 'ocid_prefix_value'
    
    # Call the main function
    main(xml_path, ocid_prefix)
    
    # Load the printed JSON output
    with open('output.json', 'r') as f:
        output_json = json.load(f)
    
    # Assert that the output contains the expected fields
    assert 'tender' in output_json
    assert 'lots' in output_json['tender']
    assert len(output_json['tender']['lots']) > 0
    for lot in output_json['tender']['lots']:
        assert 'hasSustainability' in lot
        assert lot['hasSustainability'] is True
        assert 'sustainability' in lot
        for sustainability in lot['sustainability']:
            assert 'goal' in sustainability
            assert 'strategies' in sustainability

def test_main_with_invalid_xml():
    # Path to an invalid XML file for testing
    xml_path = 'input_files/invalid_xml.xml'
    ocid_prefix = 'ocid_prefix_value'
    
    # Call the main function
    main(xml_path, ocid_prefix)
    
    # Load the printed JSON output
    with open('output.json', 'r') as f:
        output_json = json.load(f)
    
    # Assert that the output does not contain lots with sustainability information
    assert 'tender' in output_json
    assert 'lots' in output_json['tender']
    for lot in output_json['tender']['lots']:
        assert 'hasSustainability' in lot
        assert lot['hasSustainability'] is False
        assert 'sustainability' not in lot

def test_main_with_no_lots():
    # Path to an XML file with no lots for testing
    xml_path = 'input_files/no_lots_xml.xml'
    ocid_prefix = 'ocid_prefix_value'
    
    # Call the main function
    main(xml_path, ocid_prefix)
    
    # Load the printed JSON output
    with open('output.json', 'r') as f:
        output_json = json.load(f)
    
    # Assert that the output does not contain lots
    assert 'tender' in output_json
    assert 'lots' in output_json['tender']
    assert len(output_json['tender']['lots']) == 0