# tests/test_bt_01e_procedure.py

from pathlib import Path
import pytest
import json
import sys
import logging
import tempfile

# Add the parent directory to sys.path to import main
sys.path.append(str(Path(__file__).parent.parent))
from src.ted_and_doffin_to_ocds.main import main, configure_logging
from src.ted_and_doffin_to_ocds.converters.bt_01e_procedure import (
    parse_procedure_legal_basis_noid,
    merge_procedure_legal_basis_noid,
)


@pytest.fixture(scope="module")
def setup_logging():
    configure_logging()
    return logging.getLogger(__name__)


@pytest.fixture
def temp_output_dir():
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield Path(tmpdirname)


def test_bt_01e_procedure_with_locallegal(setup_logging):
    logger = setup_logging
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
              xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
              xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cbc:ID>notice-1</cbc:ID>
        <cbc:ContractFolderID>cf-1</cbc:ContractFolderID>
        <cac:TenderingTerms>
            <cac:ProcurementLegislationDocumentReference>
                <cbc:ID>LocalLegalBasis</cbc:ID>
            </cac:ProcurementLegislationDocumentReference>
        </cac:TenderingTerms>
    </ContractAwardNotice>
    """

    # Test parsing
    parsed_data = parse_procedure_legal_basis_noid(xml_content)
    logger.info("Parsed data: %s", parsed_data)
    assert parsed_data is not None
    assert "tender" in parsed_data
    assert "legalBasis" in parsed_data["tender"]
    assert parsed_data["tender"]["legalBasis"]["id"] == "LocalLegalBasis"

    # Test merging
    release_json = {"tender": {"id": "cf-1"}}
    merge_procedure_legal_basis_noid(release_json, parsed_data)
    assert "legalBasis" in release_json["tender"]
    assert "id" in release_json["tender"]["legalBasis"]
    assert release_json["tender"]["legalBasis"]["id"] == "LocalLegalBasis"


def test_bt_01e_procedure_without_locallegal():
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
              xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
              xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cbc:ID>notice-1</cbc:ID>
        <cbc:ContractFolderID>cf-1</cbc:ContractFolderID>
        <cac:TenderingTerms>
            <cac:ProcurementLegislationDocumentReference>
                <cbc:ID>OtherBasis</cbc:ID>
            </cac:ProcurementLegislationDocumentReference>
        </cac:TenderingTerms>
    </ContractAwardNotice>
    """

    # Should not include non-LocalLegalBasis references
    parsed_data = parse_procedure_legal_basis_noid(xml_content)
    assert parsed_data is None


def test_bt_01e_procedure_integration(tmp_path, setup_logging, temp_output_dir):
    logger = setup_logging
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
              xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
              xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cbc:ID>notice-1</cbc:ID>
        <cbc:ContractFolderID>cf-1</cbc:ContractFolderID>
        <cac:TenderingTerms>
            <cac:ProcurementLegislationDocumentReference>
                <cbc:ID>LocalLegalBasis</cbc:ID>
            </cac:ProcurementLegislationDocumentReference>
        </cac:TenderingTerms>
    </ContractAwardNotice>
    """
    xml_file = tmp_path / "test_input_with_locallegal.xml"
    xml_file.write_text(xml_content)

    result = run_main_and_get_result(xml_file, temp_output_dir)
    logger.info("Test result: %s", json.dumps(result, indent=2))

    assert "tender" in result
    assert "legalBasis" in result["tender"]
    assert result["tender"]["legalBasis"]["id"] == "LocalLegalBasis"


def run_main_and_get_result(xml_file, output_dir):
    main(str(xml_file), str(output_dir), "ocds-test-prefix", "test-scheme")
    output_files = list(output_dir.glob("*_release_0.json"))
    assert len(output_files) == 1, f"Expected 1 output file, got {len(output_files)}"
    with output_files[0].open() as f:
        return json.load(f)


if __name__ == "__main__":
    pytest.main(["-v"])
