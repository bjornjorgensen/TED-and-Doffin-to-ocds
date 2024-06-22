# tests/test_BT_03.py
import sys
import os
import subprocess
import json
from lxml import etree

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from converters.BT_03 import parse_form_type

def test_parse_form_type():
    # Sample XML content for testing
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cbc:NoticeTypeCode listName="competition">cn-standard</cbc:NoticeTypeCode>
    </root>
    """
    tree = etree.fromstring(xml_content)
    xml_content = etree.tostring(tree, encoding='utf-8')

    result = parse_form_type(xml_content)

    assert result == {
        "tag": ["tender"],
        "tender": {
            "status": "active"
        }
    }

# Add more tests as needed

def test_main_execution():
    # Path to the test XML file
    xml_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'input_files', 'test_notice.xml'))
    # Prefix for OCID
    ocid_prefix = 'ocid_prefix_value'

    # Call main.py with the specified arguments
    result = subprocess.run([sys.executable, 'main.py', xml_path, ocid_prefix], capture_output=True, text=True)

    # Decode the output
    output = result.stdout

    # Parse the JSON output
    try:
        json_output = json.loads(output)
    except json.JSONDecodeError:
        assert False, f"Output is not valid JSON: {output}"

    # Add assertions to check the expected output
    assert "tag" in json_output, "Missing 'tag' in output"
    assert "tender" in json_output, "Missing 'tender' in output"
    assert json_output["tender"]["status"] == "complete", "Unexpected tender status"

# Add more tests as needed