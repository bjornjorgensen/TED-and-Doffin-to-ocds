# tests/test_BT_127_notice.py

import pytest
import json
import os
import sys
import logging

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main

def test_bt_127_notice_integration(tmp_path, caplog):
    caplog.set_level(logging.INFO)

    xml_content = """
    <root xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cbc:PlannedDate>2020-03-15+01:00</cbc:PlannedDate>
    </root>
    """
    xml_file = tmp_path / "test_input_future_notice.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    print("Log messages:")
    for record in caplog.records:
        print(f"{record.levelname}: {record.message}")

    with open('output.json', 'r') as f:
        result = json.load(f)

    print("Full result:")
    print(json.dumps(result, indent=2))

    assert "tender" in result, "tender object not found in the result"
    assert "communication" in result["tender"], "communication object not found in tender"
    assert "futureNoticeDate" in result["tender"]["communication"], "futureNoticeDate not found in communication"
    assert result["tender"]["communication"]["futureNoticeDate"] == "2020-03-15T00:00:00+01:00"

if __name__ == "__main__":
    pytest.main(['-v', '-s'])