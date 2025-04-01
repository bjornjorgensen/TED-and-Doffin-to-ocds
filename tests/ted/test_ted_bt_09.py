# tests/ted/test_ted_bt_09.py

import json
import logging
import sys
import tempfile
from pathlib import Path

import pytest

# Add the parent directory to sys.path to import main
sys.path.append(str(Path(__file__).parent.parent.parent))
from src.ted_and_doffin_to_ocds.main import main


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


def test_ted_bt_09_cross_border_law(tmp_path, setup_logging, temp_output_dir) -> None:
    # TED format XML with Cross Border Law information
    ted_xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <TED_EXPORT>
        <FORM_SECTION>
            <F03_2014>
                <CONTRACTING_BODY>
                    <PROCUREMENT_LAW>Directive XYZ on Cross Border Law for TED Format</PROCUREMENT_LAW>
                </CONTRACTING_BODY>
            </F03_2014>
        </FORM_SECTION>
    </TED_EXPORT>
    """

    # Create input TED XML file
    xml_file = tmp_path / "test_ted_input_cross_border_law.xml"
    xml_file.write_text(ted_xml_content)

    # Run main and get result
    result = run_main_and_get_result(xml_file, temp_output_dir)

    # Verify the results
    assert "tender" in result, "Expected 'tender' in result"
    assert "crossBorderLaw" in result["tender"], "Expected 'crossBorderLaw' in tender"
    assert (
        result["tender"]["crossBorderLaw"] == "Directive XYZ on Cross Border Law for TED Format"
    ), "Unexpected crossBorderLaw value"


def test_ted_bt_09_multiple_forms(tmp_path, setup_logging, temp_output_dir) -> None:
    # Test with different TED form formats that contain the PROCUREMENT_LAW field
    ted_xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <TED_EXPORT>
        <FORM_SECTION>
            <F02_2014>
                <CONTRACTING_BODY>
                    <PROCUREMENT_LAW>Directive ABC on Cross Border Law (F02)</PROCUREMENT_LAW>
                </CONTRACTING_BODY>
            </F02_2014>
        </FORM_SECTION>
    </TED_EXPORT>
    """

    # Create input TED XML file
    xml_file = tmp_path / "test_ted_input_cross_border_law_f02.xml"
    xml_file.write_text(ted_xml_content)

    # Run main and get result
    result = run_main_and_get_result(xml_file, temp_output_dir)

    # Verify the results
    assert "tender" in result, "Expected 'tender' in result"
    assert "crossBorderLaw" in result["tender"], "Expected 'crossBorderLaw' in tender"
    assert (
        result["tender"]["crossBorderLaw"] == "Directive ABC on Cross Border Law (F02)"
    ), "Unexpected crossBorderLaw value"


def test_ted_bt_09_cross_border_law_missing(
    tmp_path, setup_logging, temp_output_dir
) -> None:
    # TED format XML without Cross Border Law information
    ted_xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <TED_EXPORT>
        <FORM_SECTION>
            <F03_2014>
                <CONTRACTING_BODY>
                    <!-- PROCUREMENT_LAW element intentionally missing -->
                </CONTRACTING_BODY>
            </F03_2014>
        </FORM_SECTION>
    </TED_EXPORT>
    """

    # Create input TED XML file
    xml_file = tmp_path / "test_ted_input_cross_border_law_missing.xml"
    xml_file.write_text(ted_xml_content)

    # Run main and get result
    result = run_main_and_get_result(xml_file, temp_output_dir)

    # Verify the results
    assert "tender" not in result or "crossBorderLaw" not in result.get(
        "tender", {}
    ), "Unexpected 'crossBorderLaw' in result when missing in input"


if __name__ == "__main__":
    pytest.main(["-v"])
