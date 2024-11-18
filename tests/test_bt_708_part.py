# tests/test_bt_708_part.py
from pathlib import Path
import pytest
import json
import sys
import logging
import tempfile

# Add the parent directory to sys.path to import main
sys.path.append(str(Path(__file__).parent.parent))
from src.ted_and_doffin_to_ocds.main import main, configure_logging


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


def test_bt_708_part_integration(tmp_path, setup_logging, temp_output_dir):
    logger = setup_logging

    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
          xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
          xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1">
        <cbc:ID>notice-1234</cbc:ID>
        <cbc:IssueDate>2023-01-01</cbc:IssueDate>
        <cbc:IssueTime>12:00:00Z</cbc:IssueTime>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Part">part-1</cbc:ID>
            <cac:TenderingTerms>
                <cac:CallForTendersDocumentReference>
                    <cbc:ID>doc-1</cbc:ID>
                    <ext:UBLExtensions>
                        <ext:UBLExtension>
                            <ext:ExtensionContent>
                                <efext:EformsExtension>
                                    <efac:OfficialLanguages>
                                        <cac:Language>
                                            <cbc:ID>ENG</cbc:ID>
                                        </cac:Language>
                                        <cac:Language>
                                            <cbc:ID>FRA</cbc:ID>
                                        </cac:Language>
                                    </efac:OfficialLanguages>
                                </efext:EformsExtension>
                            </ext:ExtensionContent>
                        </ext:UBLExtension>
                    </ext:UBLExtensions>
                </cac:CallForTendersDocumentReference>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </ContractAwardNotice>
    """
    xml_file = tmp_path / "test_input_bt_708_part.xml"
    xml_file.write_text(xml_content)

    result = run_main_and_get_result(xml_file, temp_output_dir)
    logger.info("Result: %s", json.dumps(result, indent=2))

    # Check tender and documents exist
    assert "tender" in result, "Expected 'tender' in result"
    assert "documents" in result["tender"], "Expected 'documents' in tender"
    assert len(result["tender"]["documents"]) == 1, "Expected 1 document"

    # Check document languages
    document = result["tender"]["documents"][0]
    assert (
        document["id"] == "doc-1"
    ), f"Expected document id 'doc-1', got {document['id']}"
    assert "languages" in document, "Expected 'languages' in document"
    assert sorted(document["languages"]) == [
        "en",
        "fr",
    ], f"Expected languages ['en', 'fr'], got {document['languages']}"

    logger.info("Test bt_708_part_integration passed successfully.")


if __name__ == "__main__":
    pytest.main(["-v", "-s"])
