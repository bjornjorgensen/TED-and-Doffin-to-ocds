# tests/test_bt_125_part.py
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
    output_files = list(output_dir.glob("*.json"))
    assert len(output_files) == 1, f"Expected 1 output file, got {len(output_files)}"
    with output_files[0].open() as f:
        return json.load(f)


@pytest.mark.parametrize("caplog", [True], indirect=True)
def test_bt_125_part_integration(tmp_path, temp_output_dir, caplog) -> None:
    caplog.set_level(logging.INFO)

    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
        xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
        xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cbc:ID>notice-1</cbc:ID>
        <cbc:ContractFolderID>cf-1</cbc:ContractFolderID>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Part">PART-0001</cbc:ID>
            <cac:TenderingProcess>
                <cac:NoticeDocumentReference>
                    <cbc:ID schemeName="notice-id-ref">123e4567-e89b-12d3-a456-426614174000-06</cbc:ID>
                    <cbc:ReferencedDocumentInternalAddress>PAR-0001</cbc:ReferencedDocumentInternalAddress>
                </cac:NoticeDocumentReference>
            </cac:TenderingProcess>
        </cac:ProcurementProjectLot>
    </ContractAwardNotice>
    """

    # Create input XML file
    xml_file = tmp_path / "test_input_previous_planning_part.xml"
    xml_file.write_text(xml_content)

    # Run main and get result
    result = run_main_and_get_result(xml_file, temp_output_dir)

    # Check the log
    for _record in caplog.records:
        pass

    # Verify the results
    assert "relatedProcesses" in result
    assert len(result["relatedProcesses"]) == 2  # Expecting two related processes
    
    # Find our expected related process with the scheme eu-notice-id-ref and full identifier
    part_process = next(
        (rp for rp in result["relatedProcesses"] 
         if rp["scheme"] == "eu-notice-id-ref" and 
         rp["identifier"] == "123e4567-e89b-12d3-a456-426614174000-06-PAR-0001"),
        None
    )
    
    # Assert that we found the expected related process
    assert part_process is not None
    assert part_process["id"] == "1"
    assert part_process["relationship"] == ["planning"]
    assert part_process["scheme"] == "eu-notice-id-ref"
    assert part_process["identifier"] == "123e4567-e89b-12d3-a456-426614174000-06-PAR-0001"


if __name__ == "__main__":
    pytest.main(["-v", "-s"])
