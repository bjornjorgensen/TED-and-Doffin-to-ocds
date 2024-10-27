# tests/test_bt_01d_procedure.py

from pathlib import Path
import pytest
import json
import sys
import logging
import tempfile

# Add the parent directory to sys.path to import main
sys.path.append(str(Path(__file__).parent.parent))
from src.ted_and_doffin_to_ocds.main import main, configure_logging
from src.ted_and_doffin_to_ocds.converters.bt_01d_procedure import (
    parse_procedure_legal_basis_description,
    merge_procedure_legal_basis_description,
)


@pytest.fixture(scope="module")
def setup_logging():
    configure_logging()
    return logging.getLogger(__name__)


@pytest.fixture
def temp_output_dir():
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield Path(tmpdirname)


def test_bt_01d_procedure_with_description(setup_logging):
    logger = setup_logging
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
              xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
              xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cbc:ID>notice-1</cbc:ID>
        <cbc:ContractFolderID>cf-1</cbc:ContractFolderID>
        <cac:TenderingTerms>
            <cac:ProcurementLegislationDocumentReference>
                <cbc:DocumentDescription>Directive XYZ applies ...</cbc:DocumentDescription>
            </cac:ProcurementLegislationDocumentReference>
        </cac:TenderingTerms>
    </ContractAwardNotice>
    """

    # Test parsing
    parsed_data = parse_procedure_legal_basis_description(xml_content)
    logger.info("Parsed data: %s", parsed_data)
    assert parsed_data is not None
    assert "tender" in parsed_data
    assert "legalBasis" in parsed_data["tender"]
    assert (
        parsed_data["tender"]["legalBasis"]["description"]
        == "Directive XYZ applies ..."
    )

    # Test merging
    release_json = {"tender": {"id": "cf-1"}}
    merge_procedure_legal_basis_description(release_json, parsed_data)
    assert "legalBasis" in release_json["tender"]
    assert "description" in release_json["tender"]["legalBasis"]
    assert (
        release_json["tender"]["legalBasis"]["description"]
        == "Directive XYZ applies ..."
    )


def test_bt_01d_procedure_with_excluded_ids():
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
              xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
              xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cbc:ID>notice-1</cbc:ID>
        <cbc:ContractFolderID>cf-1</cbc:ContractFolderID>
        <cac:TenderingTerms>
            <cac:ProcurementLegislationDocumentReference>
                <cbc:ID>CrossBorderLaw</cbc:ID>
                <cbc:DocumentDescription>Should not be included</cbc:DocumentDescription>
            </cac:ProcurementLegislationDocumentReference>
        </cac:TenderingTerms>
    </ContractAwardNotice>
    """

    # Should not include description from excluded references
    parsed_data = parse_procedure_legal_basis_description(xml_content)
    assert parsed_data is None


def test_bt_01d_procedure_integration(tmp_path, setup_logging, temp_output_dir):
    logger = setup_logging
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
              xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
              xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cbc:ID>notice-1</cbc:ID>
        <cbc:ContractFolderID>cf-1</cbc:ContractFolderID>
        <cac:TenderingTerms>
            <cac:ProcurementLegislationDocumentReference>
                <cbc:DocumentDescription>Directive XYZ applies ...</cbc:DocumentDescription>
            </cac:ProcurementLegislationDocumentReference>
        </cac:TenderingTerms>
    </ContractAwardNotice>
    """
    xml_file = tmp_path / "test_input_with_description.xml"
    xml_file.write_text(xml_content)

    result = run_main_and_get_result(xml_file, temp_output_dir)
    logger.info("Test result: %s", json.dumps(result, indent=2))

    assert "tender" in result
    assert "legalBasis" in result["tender"]
    assert "description" in result["tender"]["legalBasis"]
    assert result["tender"]["legalBasis"]["description"] == "Directive XYZ applies ..."


def run_main_and_get_result(xml_file, output_dir):
    main(str(xml_file), str(output_dir), "ocds-test-prefix", "test-scheme")
    output_files = list(output_dir.glob("*_release_0.json"))
    assert len(output_files) == 1, f"Expected 1 output file, got {len(output_files)}"
    with output_files[0].open() as f:
        return json.load(f)


if __name__ == "__main__":
    pytest.main(["-v"])
