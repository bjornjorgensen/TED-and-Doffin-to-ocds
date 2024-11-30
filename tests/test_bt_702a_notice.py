# tests/test_bt_702a_notice.py
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
        path = Path(tmpdirname)
        path.mkdir(exist_ok=True)
        yield path


def run_main_and_get_result(xml_file, output_dir):
    main(str(xml_file), str(output_dir), "ocds-test-prefix", "test-scheme")
    output_files = list(output_dir.glob("*.json"))
    assert len(output_files) == 1, f"Expected 1 output file, got {len(output_files)}"
    with output_files[0].open() as f:
        return json.load(f)


def test_bt_702a_notice_integration(tmp_path, setup_logging, temp_output_dir) -> None:
    logger = setup_logging

    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractNotice-2"
                    xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cbc:noticeLanguageCode>ENG</cbc:noticeLanguageCode>
    </ContractNotice>
    """
    xml_file = tmp_path / "test_input_notice_language.xml"
    xml_file.write_text(xml_content)

    result = run_main_and_get_result(xml_file, temp_output_dir)
    logger.info("Result: %s", json.dumps(result, indent=2))

    assert "language" in result, "Expected 'language' in result"
    assert (
        result["language"] == "en"
    ), f"Expected language 'en', got {result['language']}"


def test_bt_702a_notice_integration_unknown_language(
    tmp_path, setup_logging, temp_output_dir
) -> None:
    logger = setup_logging

    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractNotice-2"
                    xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cbc:UBLVersionID>2.3</cbc:UBLVersionID>
        <cbc:CustomizationID>eforms-sdk-1.10</cbc:CustomizationID>
        <cbc:ID>notice-id</cbc:ID>
        <cbc:noticeLanguageCode>XYZ</cbc:noticeLanguageCode>
    </ContractNotice>
    """
    xml_file = tmp_path / "test_input_unknown_language.xml"
    xml_file.write_text(xml_content)

    result = run_main_and_get_result(xml_file, temp_output_dir)
    logger.info("Result: %s", json.dumps(result, indent=2))

    # Don't assert language field must exist since it's removed when invalid
    if "language" in result:
        assert (
            result["language"] == "und"
        ), f"Expected language 'und', got {result['language']}"


if __name__ == "__main__":
    pytest.main(["-v", "-s"])
