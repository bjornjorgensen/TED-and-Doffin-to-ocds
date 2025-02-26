# tests/test_bt_615_lot.py
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
    main(str(xml_file), str(output_dir), "ocds-test-prefix", "test-scheme")
    output_files = list(output_dir.glob("*_release_0.json"))
    assert len(output_files) == 1, f"Expected 1 output file, got {len(output_files)}"
    with output_files[0].open() as f:
        return json.load(f)


def test_bt_615_lot_integration(tmp_path, setup_logging, temp_output_dir) -> None:
    logger = setup_logging
    xml_content = """
    <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
          xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:TenderingTerms>
                <cac:CallForTendersDocumentReference>
                    <cbc:ID>20210521/CTFD/ENG/7654-02</cbc:ID>
                    <cbc:DocumentType>restricted-document</cbc:DocumentType>
                    <cac:Attachment>
                        <cac:ExternalReference>
                            <cbc:URI>https://mywebsite.com/proc/2019024/accessinfo</cbc:URI>
                        </cac:ExternalReference>
                    </cac:Attachment>
                </cac:CallForTendersDocumentReference>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </ContractAwardNotice>
    """
    xml_file = tmp_path / "test_input_documents_restricted_url.xml"
    xml_file.write_text(xml_content)

    # Run main and get result
    result = run_main_and_get_result(xml_file, temp_output_dir)

    # logger.info("Result: %s", json.dumps(result, indent=2) # Logging disabled)

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
        document["accessDetailsURL"] == "https://mywebsite.com/proc/2019024/accessinfo"
    ), f"Expected accessDetailsURL 'https://mywebsite.com/proc/2019024/accessinfo', got {document['accessDetailsURL']}"
    assert document["relatedLots"] == [
        "LOT-0001",
    ], f"Expected relatedLots ['LOT-0001'], got {document['relatedLots']}"

    # logger.info("Test bt_615_lot_integration passed successfully.") # Logging disabled


if __name__ == "__main__":
    pytest.main(["-v", "-s"])
