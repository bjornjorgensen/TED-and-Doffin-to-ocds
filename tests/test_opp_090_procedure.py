# tests/test_OPP_090_procedure.py
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
    output_files = list(output_dir.glob("*.json"))
    assert len(output_files) == 1, f"Expected 1 output file, got {len(output_files)}"
    with output_files[0].open() as f:
        return json.load(f)


def test_opp_090_procedure_integration(tmp_path, setup_logging, temp_output_dir):
    logger = setup_logging

    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
        xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
        xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cbc:ID>notice-1</cbc:ID>
        <cbc:ContractFolderID>cf-1</cbc:ContractFolderID>
        <cac:TenderingProcess>
            <cac:noticeDocumentReference>
                <cbc:ID schemeName="notice-id-ref">123e4567-e89b-12d3-a456-426614174000-06</cbc:ID>
            </cac:noticeDocumentReference>
        </cac:TenderingProcess>
        <cac:TenderingProcess>
            <cac:noticeDocumentReference>
                <cbc:ID schemeName="notice-id-ref">987e6543-e21b-12d3-a456-426614174000-07</cbc:ID>
            </cac:noticeDocumentReference>
        </cac:TenderingProcess>
    </ContractAwardNotice>
    """

    # Create input XML file
    xml_file = tmp_path / "test_input_previous_notice_identifier.xml"
    xml_file.write_text(xml_content)

    # Run main and get result
    result = run_main_and_get_result(xml_file, temp_output_dir)

    logger.info("Test result: %s", json.dumps(result, indent=2))

    # Verify the results
    assert "relatedProcesses" in result
    assert len(result["relatedProcesses"]) == 2

    related_process_1 = result["relatedProcesses"][0]
    assert related_process_1["id"] == "1"
    assert related_process_1["relationship"] == ["planning"]
    assert related_process_1["scheme"] == "eu-oj"
    assert related_process_1["identifier"] == "123e4567-e89b-12d3-a456-426614174000-06"

    related_process_2 = result["relatedProcesses"][1]
    assert related_process_2["id"] == "2"
    assert related_process_2["relationship"] == ["planning"]
    assert related_process_2["scheme"] == "eu-oj"
    assert related_process_2["identifier"] == "987e6543-e21b-12d3-a456-426614174000-07"


if __name__ == "__main__":
    pytest.main(["-v"])
