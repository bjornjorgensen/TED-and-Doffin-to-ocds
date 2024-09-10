# tests/test_BT_05_Notice.py

import pytest
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.ted_and_doffin_to_ocds.main import main


def test_bt_05_notice_integration(tmp_path):
    xml_content = """
    <root xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cbc:IssueDate>2019-11-26+01:00</cbc:IssueDate>
        <cbc:IssueTime>13:38:54+01:00</cbc:IssueTime>
    </root>
    """
    xml_file = tmp_path / "test_input_notice_dispatch_date_time.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open("output.json") as f:
        result = json.load(f)

    assert "date" in result
    assert result["date"] == "2019-11-26T13:38:54+01:00"


if __name__ == "__main__":
    pytest.main()
