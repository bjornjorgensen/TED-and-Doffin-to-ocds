# tests/test_bt_01_procedure.py

from pathlib import Path
import pytest
import json
import sys
import logging
import tempfile

# Add the parent directory to sys.path to import main
sys.path.append(str(Path(__file__).parent.parent))
from src.ted_and_doffin_to_ocds.main import main, configure_logging, process_bt_section
from src.ted_and_doffin_to_ocds.converters.bt_01_procedure import (
    parse_procedure_legal_basis,
    merge_procedure_legal_basis,
)


@pytest.fixture(scope="module")
def setup_logging():
    configure_logging()
    return logging.getLogger(__name__)


@pytest.fixture
def temp_output_dir():
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield Path(tmpdirname)


def test_parser_directly(setup_logging):
    logger = setup_logging
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
              xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
              xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cbc:ID>notice-1</cbc:ID>
        <cbc:ContractFolderID>cf-1</cbc:ContractFolderID>
        <cac:TenderingTerms>
            <cac:ProcurementLegislationDocumentReference>
                <cbc:ID>FOA § 13-4 bokstav b annet punkt</cbc:ID>
            </cac:ProcurementLegislationDocumentReference>
        </cac:TenderingTerms>
    </ContractAwardNotice>
    """

    # Test parser directly
    parsed_data = parse_procedure_legal_basis(xml_content)
    logger.info("Parser output: %s", parsed_data)

    # Test processor directly
    release_json = {"tender": {"id": "cf-1"}}
    process_bt_section(
        release_json,
        xml_content,
        [parse_procedure_legal_basis],
        merge_procedure_legal_basis,
        "procedure Legal Basis (BT-01)",
    )
    logger.info("Process output: %s", json.dumps(release_json, indent=2))


def test_bt_01_procedure_steps(setup_logging):
    logger = setup_logging
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
              xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
              xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cbc:ID>notice-1</cbc:ID>
        <cbc:ContractFolderID>cf-1</cbc:ContractFolderID>
        <cac:TenderingTerms>
            <cac:ProcurementLegislationDocumentReference>
                <cbc:ID schemeName="ELI">FOA § 13-4 bokstav b annet punkt</cbc:ID>
            </cac:ProcurementLegislationDocumentReference>
        </cac:TenderingTerms>
    </ContractAwardNotice>
    """

    # Step 1: Check parsing
    parsed_data = parse_procedure_legal_basis(xml_content)
    logger.info("Parsed data: %s", parsed_data)
    assert parsed_data is not None, "Parser should return data"
    assert "tender" in parsed_data
    assert "legalBasis" in parsed_data["tender"]
    assert parsed_data["tender"]["legalBasis"]["scheme"] == "ELI"

    # Step 2: Check merging
    release_json = {"tender": {"id": "cf-1"}}
    merge_procedure_legal_basis(release_json, parsed_data)
    assert "legalBasis" in release_json["tender"]


def test_bt_01_procedure_with_legal_basis(tmp_path, setup_logging, temp_output_dir):
    logger = setup_logging
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
              xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
              xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cbc:ID>notice-1</cbc:ID>
        <cbc:ContractFolderID>cf-1</cbc:ContractFolderID>
        <cac:TenderingTerms>
            <cac:ProcurementLegislationDocumentReference>
                <cbc:ID schemeName="ELI">http://data.europa.eu/eli/dir/2014/24/oj</cbc:ID>
            </cac:ProcurementLegislationDocumentReference>
        </cac:TenderingTerms>
    </ContractAwardNotice>
    """
    xml_file = tmp_path / "test_input_with_legal_basis.xml"
    xml_file.write_text(xml_content)

    # Test direct parsing first
    parsed_data = parse_procedure_legal_basis(xml_content)
    logger.info("Direct parse result: %s", parsed_data)
    assert parsed_data is not None

    # Now test through main process
    result = run_main_and_get_result(xml_file, temp_output_dir)
    logger.info("Test result: %s", json.dumps(result, indent=2))

    assert "tender" in result, "Expected 'tender' in result"
    assert "legalBasis" in result["tender"], "Expected 'legalBasis' in tender"
    legal_basis = result["tender"]["legalBasis"]
    assert legal_basis["scheme"] == "ELI", "Expected scheme to be 'ELI'"
    assert (
        legal_basis["id"] == "http://data.europa.eu/eli/dir/2014/24/oj"
    ), "Unexpected legal basis ID"


def test_bt_01_procedure_non_eli_scheme(tmp_path, setup_logging, temp_output_dir):
    logger = setup_logging
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
              xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
              xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cbc:ID>notice-1</cbc:ID>
        <cbc:ContractFolderID>cf-1</cbc:ContractFolderID>
        <cac:TenderingTerms>
            <cac:ProcurementLegislationDocumentReference>
                <cbc:ID schemeName="OTHER">some-other-reference</cbc:ID>
            </cac:ProcurementLegislationDocumentReference>
        </cac:TenderingTerms>
    </ContractAwardNotice>
    """
    xml_file = tmp_path / "test_input_non_eli_scheme.xml"
    xml_file.write_text(xml_content)

    result = run_main_and_get_result(xml_file, temp_output_dir)
    logger.info("Test result: %s", json.dumps(result, indent=2))

    assert "tender" in result, "Expected 'tender' in result"
    assert (
        "legalBasis" not in result["tender"]
    ), "Should not include legal basis for non-ELI scheme"


def run_main_and_get_result(xml_file, output_dir):
    main(str(xml_file), str(output_dir), "ocds-test-prefix", "test-scheme")
    output_files = list(output_dir.glob("*_release_0.json"))
    assert len(output_files) == 1, f"Expected 1 output file, got {len(output_files)}"
    with output_files[0].open() as f:
        return json.load(f)
