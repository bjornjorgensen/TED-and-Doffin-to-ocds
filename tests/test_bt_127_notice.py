# tests/test_bt_127_notice.py
from pathlib import Path
import pytest
import json
import sys

# Add the parent directory to sys.path to import main
sys.path.append(str(Path(__file__).parent.parent))
from src.ted_and_doffin_to_ocds.main import main


def test_bt_127_notice_integration(tmp_path):
    xml_content = """
    <root xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cbc:PlannedDate>2020-03-15+01:00</cbc:PlannedDate>
    </root>
    """
    xml_file = tmp_path / "test_input_future_notice_date.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with Path("output.json").open() as f:
        result = json.load(f)

    assert "tender" in result
    assert "communication" in result["tender"]
    assert "futurenoticeDate" in result["tender"]["communication"]
    assert (
        result["tender"]["communication"]["futurenoticeDate"]
        == "2020-03-15T00:00:00+01:00"
    )


if __name__ == "__main__":
    pytest.main()
