# tests/test_BT_738_notice.py

import pytest
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main


def test_bt_738_notice_integration(tmp_path):
    xml_content = """
    <root xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cbc:RequestedPublicationDate>2020-03-15+01:00</cbc:RequestedPublicationDate>
    </root>
    """
    xml_file = tmp_path / "test_input_notice_preferred_publication_date.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open("output.json") as f:
        result = json.load(f)

    assert "tender" in result, "Expected 'tender' in result"
    assert "communication" in result["tender"], "Expected 'communication' in tender"
    assert (
        "noticePreferredPublicationDate" in result["tender"]["communication"]
    ), "Expected 'noticePreferredPublicationDate' in communication"
    assert (
        result["tender"]["communication"]["noticePreferredPublicationDate"]
        == "2020-03-15T00:00:00+01:00"
    ), f"Expected noticePreferredPublicationDate '2020-03-15T00:00:00+01:00', got {result['tender']['communication']['noticePreferredPublicationDate']}"


if __name__ == "__main__":
    pytest.main()
