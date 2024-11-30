# tests/test_bt_15_Lot_part.py
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
    configure_logging()
    return logging.getLogger(__name__)


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


def test_bt_15_lot_part_integration(tmp_path, setup_logging, temp_output_dir) -> None:
    logger = setup_logging

    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
        xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
        xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cbc:ID>notice-1</cbc:ID>
        <cbc:ContractFolderID>cf-1</cbc:ContractFolderID>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:TenderingTerms>
                <cac:CallForTendersDocumentReference>
                    <cbc:ID>20210521/CTFD/ENG/7654-02</cbc:ID>
                    <cbc:DocumentType>non-restricted-document</cbc:DocumentType>
                    <cac:Attachment>
                        <cac:ExternalReference>
                            <cbc:URI>https://mywebsite.com/proc/2019024/accessinfo</cbc:URI>
                        </cac:ExternalReference>
                    </cac:Attachment>
                </cac:CallForTendersDocumentReference>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="part">PART-0001</cbc:ID>
            <cac:TenderingTerms>
                <cac:CallForTendersDocumentReference>
                    <cbc:ID>20210521/CTFD/ENG/7654-03</cbc:ID>
                    <cbc:DocumentType>non-restricted-document</cbc:DocumentType>
                    <cac:Attachment>
                        <cac:ExternalReference>
                            <cbc:URI>https://mywebsite.com/proc/2019024/accessinfo-part</cbc:URI>
                        </cac:ExternalReference>
                    </cac:Attachment>
                </cac:CallForTendersDocumentReference>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </ContractAwardNotice>
    """

    # Create input XML file
    xml_file = tmp_path / "test_input_documents_url.xml"
    xml_file.write_text(xml_content)

    # Run main and get result
    result = run_main_and_get_result(xml_file, temp_output_dir)

    logger.info("Test result: %s", json.dumps(result, indent=2))

    # Verify the results
    assert "tender" in result, "Expected 'tender' in result"
    assert "documents" in result["tender"], "Expected 'documents' in tender"
    assert (
        len(result["tender"]["documents"]) == 2
    ), f"Expected 2 documents, got {len(result['tender']['documents'])}"

    lot_document = next(
        doc
        for doc in result["tender"]["documents"]
        if doc["id"] == "20210521/CTFD/ENG/7654-02"
    )
    assert (
        lot_document["documentType"] == "biddingDocuments"
    ), f"Expected documentType 'biddingDocuments', got {lot_document['documentType']}"
    assert (
        lot_document["url"] == "https://mywebsite.com/proc/2019024/accessinfo"
    ), "Unexpected URL for lot document"
    assert "relatedLots" in lot_document, "Expected 'relatedLots' in lot document"
    assert lot_document["relatedLots"] == [
        "LOT-0001"
    ], f"Expected relatedLots ['LOT-0001'], got {lot_document['relatedLots']}"

    part_document = next(
        doc
        for doc in result["tender"]["documents"]
        if doc["id"] == "20210521/CTFD/ENG/7654-03"
    )
    assert (
        part_document["documentType"] == "biddingDocuments"
    ), f"Expected documentType 'biddingDocuments', got {part_document['documentType']}"
    assert (
        part_document["url"] == "https://mywebsite.com/proc/2019024/accessinfo-part"
    ), "Unexpected URL for part document"
    assert (
        "relatedLots" not in part_document
    ), "Unexpected 'relatedLots' in part document"


if __name__ == "__main__":
    pytest.main(["-v"])
