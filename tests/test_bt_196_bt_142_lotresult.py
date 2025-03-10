import json
import sys
import tempfile
from pathlib import Path

import pytest

# Add the parent directory to sys.path to import main
sys.path.append(str(Path(__file__).parent.parent))
from src.ted_and_doffin_to_ocds.main import main


@pytest.fixture
def temp_output_dir():
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield Path(tmpdirname)


def run_main_and_get_result(xml_file, output_dir):
    main(str(xml_file), str(output_dir), "ocds-test-prefix", "test-scheme")
    output_files = list(output_dir.glob("*.json"))
    assert len(output_files) == 1, f"Expected 1 output file, got {len(output_files)}"
    with output_files[0].open() as f:
        return json.load(f)


def test_bt_196_bt_142_lotresult_integration(tmp_path, temp_output_dir) -> None:
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractNotice xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
        xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
        xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
        xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
        xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
        xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1">
        <ext:UBLExtensions>
            <ext:UBLExtension>
                <ext:ExtensionContent>
                    <efext:EformsExtension>
                        <efac:NoticeResult>
                            <efac:LotResult>
                                <efac:FieldsPrivacy>
                                    <efbc:FieldIdentifierCode>win-cho</efbc:FieldIdentifierCode>
                                    <efbc:ReasonDescription>Information delayed publication because of ...</efbc:ReasonDescription>
                                </efac:FieldsPrivacy>
                                <cbc:ID schemeName="result">RES-0001</cbc:ID>
                            </efac:LotResult>
                        </efac:NoticeResult>
                    </efext:EformsExtension>
                </ext:ExtensionContent>
            </ext:UBLExtension>
        </ext:UBLExtensions>
    </ContractNotice>
    """
    xml_file = tmp_path / "test_input_bt196_bt142.xml"
    xml_file.write_text(xml_content)

    result = run_main_and_get_result(xml_file, temp_output_dir)

    assert "withheldInformation" in result, "Expected 'withheldInformation' in result"
    assert (
        len(result["withheldInformation"]) == 1
    ), f"Expected 1 withheld information item, got {len(result['withheldInformation'])}"

    withheld_info = result["withheldInformation"][0]
    assert (
        withheld_info["id"] == "win-cho-RES-0001"
    ), f"Expected id 'win-cho-RES-0001', got {withheld_info['id']}"
    assert "field" in withheld_info, "Expected 'field' in withheld_info"
    assert withheld_info["field"] == "win-cho", f"Expected field 'win-cho', got {withheld_info['field']}"
    assert "name" in withheld_info, "Expected 'name' in withheld_info"
    assert withheld_info["name"] == "Winner Chosen", f"Expected name 'Winner Chosen', got {withheld_info['name']}"


def test_bt_196_bt_142_lotresult_multiple_lots(tmp_path, temp_output_dir) -> None:
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractNotice xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
        xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
        xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
        xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
        xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
        xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1">
        <ext:UBLExtensions>
            <ext:UBLExtension>
                <ext:ExtensionContent>
                    <efext:EformsExtension>
                        <efac:NoticeResult>
                            <efac:LotResult>
                                <efac:FieldsPrivacy>
                                    <efbc:FieldIdentifierCode>win-cho</efbc:FieldIdentifierCode>
                                    <efbc:ReasonDescription>Reason for lot 1</efbc:ReasonDescription>
                                </efac:FieldsPrivacy>
                                <cbc:ID schemeName="result">RES-0001</cbc:ID>
                            </efac:LotResult>
                            <efac:LotResult>
                                <efac:FieldsPrivacy>
                                    <efbc:FieldIdentifierCode>win-cho</efbc:FieldIdentifierCode>
                                    <efbc:ReasonDescription>Reason for lot 2</efbc:ReasonDescription>
                                </efac:FieldsPrivacy>
                                <cbc:ID schemeName="result">RES-0002</cbc:ID>
                            </efac:LotResult>
                        </efac:NoticeResult>
                    </efext:EformsExtension>
                </ext:ExtensionContent>
            </ext:UBLExtension>
        </ext:UBLExtensions>
    </ContractNotice>
    """
    xml_file = tmp_path / "test_input_bt196_bt142_multiple.xml"
    xml_file.write_text(xml_content)

    result = run_main_and_get_result(xml_file, temp_output_dir)

    assert "withheldInformation" in result, "Expected 'withheldInformation' in result"
    assert (
        len(result["withheldInformation"]) == 2
    ), f"Expected 2 withheld information items, got {len(result['withheldInformation'])}"

    for i, withheld_info in enumerate(result["withheldInformation"], 1):
        assert (
            withheld_info["id"] == f"win-cho-RES-000{i}"
        ), f"Expected id 'win-cho-RES-000{i}', got {withheld_info['id']}"
        assert "field" in withheld_info, f"Expected 'field' in withheld_info for lot {i}"
        assert withheld_info["field"] == "win-cho", f"Expected field 'win-cho', got {withheld_info['field']}"
        assert "name" in withheld_info, f"Expected 'name' in withheld_info for lot {i}"
        assert withheld_info["name"] == "Winner Chosen", f"Expected name 'Winner Chosen', got {withheld_info['name']}"


def test_bt_196_bt_142_lotresult_merge_existing(tmp_path, temp_output_dir) -> None:
    """Test merging with an existing withheld information entry."""
    # Create a release with an existing withheld information item
    existing_release = {
        "withheldInformation": [
            {
                "id": "win-cho-RES-0001",
                "field": "win-cho",
                "name": "Winner Chosen"
            }
        ]
    }
    
    # Create new data to merge
    new_data = {
        "withheldInformation": [
            {
                "id": "win-cho-RES-0001",  # Same ID to test merging
                "rationale": "Updated rationale",
                "rationaleMultilingual": [
                    {"text": "Updated rationale", "languageID": "ENG"},
                    {"text": "Oppdatert begrunnelse", "languageID": "NOR"}
                ]
            }
        ]
    }
    
    # Import the function directly for unit testing
    from src.ted_and_doffin_to_ocds.converters.eforms.bt_196_bt_142_lotresult import merge_bt196_bt142_unpublished_justification
    
    # Merge the data
    merge_bt196_bt142_unpublished_justification(existing_release, new_data)
    
    # Check the result
    assert len(existing_release["withheldInformation"]) == 1, "Should still have 1 entry"
    withheld_info = existing_release["withheldInformation"][0]
    
    # Check that rationale was added to the existing structure
    assert "rationale" in withheld_info, "Should have rationale added"
    assert withheld_info["rationale"] == "Updated rationale", "Rationale should be updated"
    assert "rationaleMultilingual" in withheld_info, "Should have rationaleMultilingual added"
    assert len(withheld_info["rationaleMultilingual"]) == 2, "Should have 2 language variants"
    
    # Original fields should be preserved
    assert withheld_info["field"] == "win-cho", "Original field should be preserved"
    assert withheld_info["name"] == "Winner Chosen", "Original name should be preserved"


if __name__ == "__main__":
    pytest.main(["-v", "-s"])
