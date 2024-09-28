# tests/test_bt_03.py

from pathlib import Path
import pytest
import json
import sys

# Add the parent directory to sys.path to import main
sys.path.append(str(Path(__file__).parent.parent))
from src.ted_and_doffin_to_ocds.main import main


def test_bt_03_form_type_integration(tmp_path):
    xml_content = """
    <root xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cbc:noticeTypeCode listName="competition">cn-standard</cbc:noticeTypeCode>
    </root>
    """
    xml_file = tmp_path / "test_input_form_type.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with Path("output.json").open() as f:
        result = json.load(f)

    assert "tag" in result, "Expected 'tag' in result"
    assert "tender" in result, "Expected 'tender' in result"

    assert "tender" in result["tag"], "Expected 'tender' in result['tag']"
    assert (
        result["tender"]["status"] == "active"
    ), f"Expected tender status to be 'active', got {result['tender'].get('status')}"


def test_bt_03_form_type_integration_multiple(tmp_path):
    xml_content = """
    <root xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cbc:noticeTypeCode listName="planning">pin-only</cbc:noticeTypeCode>
        <cbc:noticeTypeCode listName="result">can-standard</cbc:noticeTypeCode>
    </root>
    """
    xml_file = tmp_path / "test_input_form_type_multiple.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with Path("output.json").open() as f:
        result = json.load(f)

    assert "tag" in result, "Expected 'tag' in result"
    assert "tender" in result, "Expected 'tender' in result"

    assert set(result["tag"]) == {
        "tender",
        "award",
        "contract",
    }, f"Expected tags to be ['tender', 'award', 'contract'], got {result['tag']}"
    assert (
        result["tender"]["status"] == "complete"
    ), f"Expected tender status to be 'complete', got {result['tender'].get('status')}"


def test_bt_03_form_type_integration_invalid(tmp_path):
    xml_content = """
    <root xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cbc:noticeTypeCode listName="invalid">invalid-type</cbc:noticeTypeCode>
    </root>
    """
    xml_file = tmp_path / "test_input_form_type_invalid.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with Path("output.json").open() as f:
        result = json.load(f)

    assert "tag" not in result or "tender" not in result.get(
        "tag",
        [],
    ), "Expected no 'tender' tag for invalid form type"
    assert "status" not in result.get(
        "tender",
        {},
    ), "Expected no tender status for invalid form type"


if __name__ == "__main__":
    pytest.main()
