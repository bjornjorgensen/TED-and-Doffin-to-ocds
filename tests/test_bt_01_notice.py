# tests/test_bt_01_notice.py

from pathlib import Path
import pytest
import json
import sys
import logging
import tempfile

# Add the parent directory to sys.path to import main
sys.path.append(str(Path(__file__).parent.parent))
from src.ted_and_doffin_to_ocds.main import main, configure_logging
from src.ted_and_doffin_to_ocds.converters.bt_01_notice import (
    parse_procedure_legal_basis_regulatory,
    merge_procedure_legal_basis_regulatory,
)


@pytest.fixture(scope="module")
def setup_logging():
    configure_logging()
    return logging.getLogger(__name__)


@pytest.fixture
def temp_output_dir():
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield Path(tmpdirname)


def test_bt_01_notice_with_regulatory_domain(setup_logging):
    logger = setup_logging
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
              xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
              xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cbc:ID>notice-1</cbc:ID>
        <cbc:ContractFolderID>cf-1</cbc:ContractFolderID>
        <cbc:RegulatoryDomain>32014L0024</cbc:RegulatoryDomain>
    </ContractAwardNotice>
    """

    # Test parsing
    parsed_data = parse_procedure_legal_basis_regulatory(xml_content)
    logger.info("Parsed data: %s", parsed_data)
    assert parsed_data is not None
    assert "tender" in parsed_data
    assert "legalBasis" in parsed_data["tender"]
    assert parsed_data["tender"]["legalBasis"]["scheme"] == "CELEX"
    assert parsed_data["tender"]["legalBasis"]["id"] == "32014L0024"

    # Test merging
    release_json = {"tender": {"id": "cf-1"}}
    merge_procedure_legal_basis_regulatory(release_json, parsed_data)
    assert "legalBasis" in release_json["tender"]
    assert release_json["tender"]["legalBasis"]["scheme"] == "CELEX"
    assert release_json["tender"]["legalBasis"]["id"] == "32014L0024"


def test_bt_01_notice_without_regulatory_domain():
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
              xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
              xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cbc:ID>notice-1</cbc:ID>
        <cbc:ContractFolderID>cf-1</cbc:ContractFolderID>
    </ContractAwardNotice>
    """

    # Should return None when no regulatory domain is present
    parsed_data = parse_procedure_legal_basis_regulatory(xml_content)
    assert parsed_data is None


def test_bt_01_notice_integration(tmp_path, setup_logging, temp_output_dir):
    logger = setup_logging
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
              xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
              xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cbc:ID>notice-1</cbc:ID>
        <cbc:ContractFolderID>cf-1</cbc:ContractFolderID>
        <cbc:RegulatoryDomain>32014L0024</cbc:RegulatoryDomain>
    </ContractAwardNotice>
    """
    xml_file = tmp_path / "test_input_with_regulatory_domain.xml"
    xml_file.write_text(xml_content)

    result = run_main_and_get_result(xml_file, temp_output_dir)
    logger.info("Test result: %s", json.dumps(result, indent=2))

    assert "tender" in result
    assert "legalBasis" in result["tender"]
    assert result["tender"]["legalBasis"]["scheme"] == "CELEX"
    assert result["tender"]["legalBasis"]["id"] == "32014L0024"


def test_bt_01_notice_with_eli_priority(setup_logging):
    logger = setup_logging
    # Test that CELEX doesn't overwrite ELI
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
              xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
              xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cbc:ID>notice-1</cbc:ID>
        <cbc:ContractFolderID>cf-1</cbc:ContractFolderID>
        <cbc:RegulatoryDomain>32014L0024</cbc:RegulatoryDomain>
        <cac:TenderingTerms>
            <cac:ProcurementLegislationDocumentReference>
                <cbc:ID schemeName="ELI">http://data.europa.eu/eli/dir/2014/24/oj</cbc:ID>
            </cac:ProcurementLegislationDocumentReference>
        </cac:TenderingTerms>
    </ContractAwardNotice>
    """

    # Create release with existing ELI data
    release_json = {
        "tender": {
            "id": "cf-1",
            "legalBasis": {
                "scheme": "ELI",
                "id": "http://data.europa.eu/eli/dir/2014/24/oj",
            },
        }
    }

    # Parse and try to merge CELEX data
    parsed_data = parse_procedure_legal_basis_regulatory(xml_content)
    logger.info("Parsed CELEX data: %s", parsed_data)
    assert parsed_data is not None

    merge_procedure_legal_basis_regulatory(release_json, parsed_data)

    # Verify ELI data wasn't overwritten
    assert release_json["tender"]["legalBasis"]["scheme"] == "ELI"
    assert (
        release_json["tender"]["legalBasis"]["id"]
        == "http://data.europa.eu/eli/dir/2014/24/oj"
    )


def test_bt_01_notice_without_eli(setup_logging):
    logger = setup_logging
    # Test that CELEX is used when no ELI exists
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
              xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
              xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cbc:ID>notice-1</cbc:ID>
        <cbc:ContractFolderID>cf-1</cbc:ContractFolderID>
        <cbc:RegulatoryDomain>32014L0024</cbc:RegulatoryDomain>
    </ContractAwardNotice>
    """

    # Create release without ELI data
    release_json = {"tender": {"id": "cf-1"}}

    # Parse and merge CELEX data
    parsed_data = parse_procedure_legal_basis_regulatory(xml_content)
    logger.info("Parsed CELEX data: %s", parsed_data)
    assert parsed_data is not None

    merge_procedure_legal_basis_regulatory(release_json, parsed_data)

    # Verify CELEX data was used
    assert release_json["tender"]["legalBasis"]["scheme"] == "CELEX"
    assert release_json["tender"]["legalBasis"]["id"] == "32014L0024"


def run_main_and_get_result(xml_file, output_dir):
    main(str(xml_file), str(output_dir), "ocds-test-prefix", "test-scheme")
    output_files = list(output_dir.glob("*_release_0.json"))
    assert len(output_files) == 1, f"Expected 1 output file, got {len(output_files)}"
    with output_files[0].open() as f:
        return json.load(f)


if __name__ == "__main__":
    pytest.main(["-v"])
