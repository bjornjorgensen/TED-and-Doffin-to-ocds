import os
import sys
import subprocess
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