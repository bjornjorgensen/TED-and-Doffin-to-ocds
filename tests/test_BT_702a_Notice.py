# tests/test_BT_702a_Notice.py

import pytest
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main

def test_bt_702a_notice_integration(tmp_path):
    xml_content = """
    <root xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cbc:NoticeLanguageCode>ENG</cbc:NoticeLanguageCode>
    </root>
    """
    xml_file = tmp_path / "test_input_notice_language.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open('output.json', 'r') as f:
        result = json.load(f)

    assert "language" in result, "Expected 'language' in result"
    assert result["language"] == "en", f"Expected language 'en', got {result['language']}"

def test_bt_702a_notice_integration_unknown_language(tmp_path):
    xml_content = """
    <root xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cbc:NoticeLanguageCode>XYZ</cbc:NoticeLanguageCode>
    </root>
    """
    xml_file = tmp_path / "test_input_notice_language_unknown.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open('output.json', 'r') as f:
        result = json.load(f)

    assert "language" not in result, "Expected 'language' not to be in result for unknown language code"

if __name__ == "__main__":
    pytest.main()