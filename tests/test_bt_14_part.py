# tests/test_bt_14_part.py
import json
import logging
import sys
import tempfile
from pathlib import Path

import pytest

# Add the parent directory to sys.path to import main
sys.path.append(str(Path(__file__).parent.parent))
from src.ted_and_doffin_to_ocds.main import configure_logging, main


@pytest.fixture(scope="module")
def setup_logging():
    # Logging disabled for tests
    logger = logging.getLogger(__name__)
    logger.disabled = True
    return logger


@pytest.fixture
def temp_output_dir():
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield Path(tmpdirname)


def run_main_and_get_result(xml_file, output_dir):
    try:
        main(str(xml_file), str(output_dir), "ocds-test-prefix", "test-scheme")
        output_files = list(output_dir.glob("*_release_0.json"))
        assert (
            len(output_files) == 1
        ), f"Expected 1 output file, got {len(output_files)}"
        with output_files[0].open() as f:
            return json.load(f)
    except Exception:
        logger = logging.getLogger(__name__)
        logger.exception("Error running main")
        raise


def test_bt_14_part_integration(tmp_path, setup_logging, temp_output_dir) -> None:
    logger = setup_logging

    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
        xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
        xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cbc:ID>notice-1</cbc:ID>
        <cbc:ContractFolderID>cf-1</cbc:ContractFolderID>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Part">PART-0001</cbc:ID>
            <cac:TenderingTerms>
                <cac:CallForTendersDocumentReference>
                    <cbc:ID>20210521/CTFD/ENG/7654-02</cbc:ID>
                    <cbc:DocumentType>restricted-document</cbc:DocumentType>
                </cac:CallForTendersDocumentReference>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </ContractAwardNotice>
    """

    # Create input XML file
    xml_file = tmp_path / "test_input_part_documents_restricted.xml"
    xml_file.write_text(xml_content)

    # logger.info("Testing with file: %s", xml_file) # Logging disabled
    # logger.info("Output directory: %s", temp_output_dir) # Logging disabled

    # Run main and get result
    result = run_main_and_get_result(xml_file, temp_output_dir)

    # logger.info("Test result: %s", json.dumps(result, indent=2) # Logging disabled)

    # Verify the results
    assert "tender" in result, "Expected 'tender' in result"
    assert "documents" in result["tender"], "Expected 'documents' in tender"
    assert (
        len(result["tender"]["documents"]) == 1
    ), f"Expected 1 document, got {len(result['tender']['documents'])}"
    document = result["tender"]["documents"][0]
    assert (
        document["id"] == "20210521/CTFD/ENG/7654-02"
    ), f"Expected document id '20210521/CTFD/ENG/7654-02', got {document['id']}"
    assert (
        document["documentType"] == "biddingDocuments"
    ), f"Expected documentType 'biddingDocuments', got {document['documentType']}"
    assert (
        document["accessDetails"] == "Restricted."
    ), f"Expected accessDetails 'Restricted.', got {document['accessDetails']}"


if __name__ == "__main__":
    pytest.main(["-v"])
