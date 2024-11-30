# tests/test_bt_737_Lot.py
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
    output_files = list(output_dir.glob("*.json"))
    assert len(output_files) == 1, f"Expected 1 output file, got {len(output_files)}"
    with output_files[0].open() as f:
        return json.load(f)


def test_bt_737_lot_integration(tmp_path, setup_logging, temp_output_dir) -> None:
    logger = setup_logging
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<ContractNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractNotice-2"
    xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
    xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
    xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
    xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
    xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1">
    <cac:ProcurementProjectLot>
        <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
        <cac:TenderingTerms>
            <cac:CallForTendersDocumentReference>
                <cbc:ID>20210521/CTFD/ENG/7654-02</cbc:ID>
                <ext:UBLExtensions>
                    <ext:UBLExtension>
                        <ext:ExtensionContent>
                            <efext:EformsExtension>
                                <efac:NonOfficialLanguages>
                                    <cac:Language>
                                        <cbc:ID>ENG</cbc:ID>
                                    </cac:Language>
                                    <cac:Language>
                                        <cbc:ID>FRA</cbc:ID>
                                    </cac:Language>
                                </efac:NonOfficialLanguages>
                            </efext:EformsExtension>
                        </ext:ExtensionContent>
                    </ext:UBLExtension>
                </ext:UBLExtensions>
            </cac:CallForTendersDocumentReference>
        </cac:TenderingTerms>
    </cac:ProcurementProjectLot>
</ContractNotice>
"""
    xml_file = tmp_path / "test_input_documents_unofficial_language.xml"
    xml_file.write_text(xml_content)
    logger.info("Created XML file at %s", xml_file)
    logger.info("Output directory: %s", temp_output_dir)

    result = run_main_and_get_result(xml_file, temp_output_dir)
    logger.info("Result: %s", json.dumps(result, indent=2))

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
        "unofficialTranslations" in document
    ), "Expected 'unofficialTranslations' in document"
    assert (
        set(document["unofficialTranslations"]) == {"en", "fr"}
    ), f"Expected unofficial translations ['en', 'fr'], got {document['unofficialTranslations']}"
    assert "relatedLots" in document, "Expected 'relatedLots' in document"
    assert document["relatedLots"] == [
        "LOT-0001"
    ], f"Expected related lots ['LOT-0001'], got {document['relatedLots']}"


if __name__ == "__main__":
    pytest.main(["-v", "-s"])
