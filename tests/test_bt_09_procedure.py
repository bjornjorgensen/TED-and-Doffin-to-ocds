# tests/test_bt_09_procedure.py

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
    output_files = list(output_dir.glob("*_release_0.json"))
    assert len(output_files) == 1, f"Expected 1 output file, got {len(output_files)}"
    with output_files[0].open() as f:
        return json.load(f)


def test_bt_09_procedure_integration(tmp_path, temp_output_dir) -> None:
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
        xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
        xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cbc:ID>notice-1</cbc:ID>
        <cbc:ContractFolderID>cf-1</cbc:ContractFolderID>
        <cac:TenderingTerms>
            <cac:ProcurementLegislationDocumentReference>
                <cbc:ID>CrossBorderLaw</cbc:ID>
                <cbc:DocumentDescription languageID="ENG">Directive XYZ on Cross Border ...</cbc:DocumentDescription>
            </cac:ProcurementLegislationDocumentReference>
        </cac:TenderingTerms>
    </ContractAwardNotice>
    """

    # Create input XML file
    xml_file = tmp_path / "test_input_cross_border_law.xml"
    xml_file.write_text(xml_content)

    # Run main and get result
    result = run_main_and_get_result(xml_file, temp_output_dir)

    # Verify the results
    assert "tender" in result, "Expected 'tender' in result"
    assert "crossBorderLaw" in result["tender"], "Expected 'crossBorderLaw' in tender"
    assert (
        result["tender"]["crossBorderLaw"] == "Directive XYZ on Cross Border ..."
    ), "Unexpected crossBorderLaw value"


def test_bt_09_procedure_integration_missing(tmp_path, temp_output_dir) -> None:
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
        xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
        xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cbc:ID>notice-1</cbc:ID>
        <cbc:ContractFolderID>cf-1</cbc:ContractFolderID>
        <cac:TenderingTerms>
        </cac:TenderingTerms>
    </ContractAwardNotice>
    """

    # Create input XML file
    xml_file = tmp_path / "test_input_cross_border_law_missing.xml"
    xml_file.write_text(xml_content)

    # Run main and get result
    result = run_main_and_get_result(xml_file, temp_output_dir)

    # Verify the results
    assert "tender" not in result or "crossBorderLaw" not in result.get(
        "tender", {}
    ), "Unexpected 'crossBorderLaw' in result when missing in input"


if __name__ == "__main__":
    pytest.main(["-v"])
