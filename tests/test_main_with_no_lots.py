import os
import sys
import subprocess
import json
from main import main

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
    assert 'lots' not in output_json['tender']