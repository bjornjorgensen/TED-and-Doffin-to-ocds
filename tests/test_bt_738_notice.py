# tests/test_bt_738_notice.py
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


def test_bt_738_notice_integration(tmp_path, setup_logging, temp_output_dir) -> None:
    logger = setup_logging
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractNotice-2"
        xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
        xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cbc:RequestedPublicationDate>2020-03-15+01:00</cbc:RequestedPublicationDate>
    </ContractNotice>
    """
    xml_file = tmp_path / "test_input_notice_preferred_publication_date.xml"
    xml_file.write_text(xml_content)
    # logger.info("Created XML file at %s", xml_file) # Logging disabled
    # logger.info("Output directory: %s", temp_output_dir) # Logging disabled
    result = run_main_and_get_result(xml_file, temp_output_dir)
    # logger.info("Result: %s", json.dumps(result, indent=2) # Logging disabled)

    assert "tender" in result, "Expected 'tender' in result"
    assert "communication" in result["tender"], "Expected 'communication' in tender"
    assert (
        "noticePreferredPublicationDate" in result["tender"]["communication"]
    ), "Expected 'noticePreferredPublicationDate' in communication"
    assert (
        result["tender"]["communication"]["noticePreferredPublicationDate"]
        == "2020-03-15T00:00:00+01:00"
    ), f"Expected noticePreferredPublicationDate '2020-03-15T00:00:00+01:00', got {result['tender']['communication']['noticePreferredPublicationDate']}"


if __name__ == "__main__":
    pytest.main(["-v", "-s"])
