# tests/test_bt_21_part.py
import json
import sys
import tempfile
from pathlib import Path

import pytest

# Add the parent directory to sys.path to import main
sys.path.append(str(Path(__file__).parent.parent))
from src.ted_and_doffin_to_ocds.main import main
from src.ted_and_doffin_to_ocds.converters.eforms.bt_21_part import parse_part_title, merge_part_title


@pytest.fixture
def temp_output_dir():
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield Path(tmpdirname)


def run_main_and_get_result(xml_file, output_dir):
    main(str(xml_file), str(output_dir), "ocds-test-prefix", "test-scheme")
    output_files = list(output_dir.glob("*_release_0.json"))
    assert len(output_files) == 1, f"Expected 1 output file, got {len(output_files)}"
    with output_files[0].open() as f:
        return json.load(f)


def test_parse_part_title_with_language():
    """Test the parser directly to ensure it extracts title with language."""
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
        xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
        xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cbc:ID>notice-1</cbc:ID>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Part">PART-0001</cbc:ID>
            <cac:ProcurementProject>
                <cbc:Name languageID="ENG">Computer Network extension</cbc:Name>
            </cac:ProcurementProject>
        </cac:ProcurementProjectLot>
    </ContractAwardNotice>
    """
    
    result = parse_part_title(xml_content)
    
    assert result is not None
    assert "tender" in result
    assert "title" in result["tender"]
    assert result["tender"]["title"] == "Computer Network extension"
    assert "titleLanguage" in result["tender"]
    assert result["tender"]["titleLanguage"] == "ENG"


def test_parse_part_title_no_language():
    """Test the parser directly for case without language."""
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
        xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
        xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cbc:ID>notice-1</cbc:ID>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Part">PART-0001</cbc:ID>
            <cac:ProcurementProject>
                <cbc:Name>Computer Network extension</cbc:Name>
            </cac:ProcurementProject>
        </cac:ProcurementProjectLot>
    </ContractAwardNotice>
    """
    
    result = parse_part_title(xml_content)
    
    assert result is not None
    assert "tender" in result
    assert "title" in result["tender"]
    assert result["tender"]["title"] == "Computer Network extension"
    assert "titleLanguage" not in result["tender"]


def test_merge_part_title():
    """Test the merge function works correctly with all fields."""
    release_json = {"tender": {"id": "test-id"}}
    part_title_data = {
        "tender": {
            "title": "Computer Network extension", 
            "titleLanguage": "ENG"
        }
    }
    
    merge_part_title(release_json, part_title_data)
    
    assert "title" in release_json["tender"]
    assert release_json["tender"]["title"] == "Computer Network extension"
    assert "titleLanguage" in release_json["tender"]
    assert release_json["tender"]["titleLanguage"] == "ENG"


def test_merge_part_title_no_language():
    """Test the merge function works correctly without language field."""
    release_json = {"tender": {"id": "test-id"}}
    part_title_data = {
        "tender": {
            "title": "Computer Network extension"
        }
    }
    
    merge_part_title(release_json, part_title_data)
    
    assert "title" in release_json["tender"]
    assert release_json["tender"]["title"] == "Computer Network extension"
    assert "titleLanguage" not in release_json["tender"]


def test_bt_21_part_integration(tmp_path, temp_output_dir) -> None:
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
        xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
        xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cbc:ID>notice-1</cbc:ID>
        <cbc:ContractFolderID>cf-1</cbc:ContractFolderID>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Part">PART-0001</cbc:ID>
            <cac:ProcurementProject>
                <cbc:Name languageID="ENG">Computer Network extension</cbc:Name>
            </cac:ProcurementProject>
        </cac:ProcurementProjectLot>
    </ContractAwardNotice>
    """

    # Create input XML file
    xml_file = tmp_path / "test_input_part_title.xml"
    xml_file.write_text(xml_content)

    # Run main and get result
    result = run_main_and_get_result(xml_file, temp_output_dir)

    # Verify the results
    assert "tender" in result
    assert "title" in result["tender"]
    assert result["tender"]["title"] == "Computer Network extension"
    # Check that titleLanguage is present and has the correct value
    assert "titleLanguage" in result["tender"]
    assert result["tender"]["titleLanguage"] == "ENG"


# Add a test for when no language ID is provided
def test_bt_21_part_no_language(tmp_path, temp_output_dir) -> None:
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
        xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
        xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cbc:ID>notice-1</cbc:ID>
        <cbc:ContractFolderID>cf-1</cbc:ContractFolderID>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Part">PART-0001</cbc:ID>
            <cac:ProcurementProject>
                <cbc:Name>Computer Network extension</cbc:Name>
            </cac:ProcurementProject>
        </cac:ProcurementProjectLot>
    </ContractAwardNotice>
    """

    # Create input XML file
    xml_file = tmp_path / "test_input_part_title_no_lang.xml"
    xml_file.write_text(xml_content)

    # Run main and get result
    result = run_main_and_get_result(xml_file, temp_output_dir)

    # Verify the results
    assert "tender" in result
    assert "title" in result["tender"]
    assert result["tender"]["title"] == "Computer Network extension"
    # Check that titleLanguage is not present when no language is specified
    assert "titleLanguage" not in result["tender"]


if __name__ == "__main__":
    pytest.main(["-v"])
