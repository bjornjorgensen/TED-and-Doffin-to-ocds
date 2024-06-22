import os
import sys
import subprocess
import json
from main import main

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