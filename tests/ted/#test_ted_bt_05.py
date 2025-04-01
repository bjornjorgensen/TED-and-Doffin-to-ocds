"""Tests for TED BT-05 Notice Dispatch Date converter."""

import json
import sys
import tempfile
from pathlib import Path

import pytest
from lxml import etree

# Add the parent directory to sys.path to import modules
sys.path.append(str(Path(__file__).parent.parent.parent))
from src.ted_and_doffin_to_ocds.converters.TED.ted_bt_05 import (
    convert_to_iso_format,
    merge_notice_dispatch_date,
    parse_notice_dispatch_date,
)
from src.ted_and_doffin_to_ocds.main import main


@pytest.fixture
def temp_output_dir():
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield Path(tmpdirname)


def test_convert_to_iso_format():
    """Test date string conversion to ISO format."""
    # Test standard date format
    assert convert_to_iso_format("2020-05-15") == "2020-05-15T00:00:00+00:00"
    
    # Test date with timezone
    assert convert_to_iso_format("2020-05-15T12:30:00+01:00") == "2020-05-15T12:30:00+01:00"
    
    # Test date with Z timezone
    assert convert_to_iso_format("2020-05-15T12:30:00Z") == "2020-05-15T12:30:00+00:00"
    
    # Test alternative date formats
    assert convert_to_iso_format("20200515") == "2020-05-15T00:00:00+00:00"
    assert convert_to_iso_format("15.05.2020") == "2020-05-15T00:00:00+00:00"
    
    # Test invalid date format
    with pytest.raises(ValueError, match="Invalid date format"):
        convert_to_iso_format("invalid-date")


def test_merge_notice_dispatch_date():
    """Test merging notice dispatch date into release JSON."""
    release_json = {}
    
    # Test with valid date
    merge_notice_dispatch_date(release_json, "2020-05-15T12:30:45+01:00")
    assert release_json["date"] == "2020-05-15T12:30:45+01:00"
    
    # Test with None
    release_json = {}
    merge_notice_dispatch_date(release_json, None)
    assert "date" not in release_json


def test_parse_notice_dispatch_date_f02():
    """Test parsing dispatch date from F02 form."""
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <TED_EXPORT>
        <FORM_SECTION>
            <F02_2014>
                <COMPLEMENTARY_INFO>
                    <DATE_DISPATCH_NOTICE>2020-05-15</DATE_DISPATCH_NOTICE>
                </COMPLEMENTARY_INFO>
            </F02_2014>
        </FORM_SECTION>
    </TED_EXPORT>
    """
    result = parse_notice_dispatch_date(xml_content)
    assert result == "2020-05-15T00:00:00+00:00"


def test_parse_notice_dispatch_date_f03():
    """Test parsing dispatch date from F03 form."""
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <TED_EXPORT>
        <FORM_SECTION>
            <F03_2014>
                <COMPLEMENTARY_INFO>
                    <DATE_DISPATCH_NOTICE>2020-06-20</DATE_DISPATCH_NOTICE>
                </COMPLEMENTARY_INFO>
            </F03_2014>
        </FORM_SECTION>
    </TED_EXPORT>
    """
    result = parse_notice_dispatch_date(xml_content)
    assert result == "2020-06-20T00:00:00+00:00"


def test_parse_notice_dispatch_date_defence():
    """Test parsing dispatch date from defence form."""
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <TED_EXPORT>
        <FORM_SECTION>
            <PRIOR_INFORMATION_DEFENCE>
                <FD_PRIOR_INFORMATION_DEFENCE>
                    <OTH_INFO_PRIOR_INFORMATION>
                        <NOTICE_DISPATCH_DATE>2020-07-30</NOTICE_DISPATCH_DATE>
                    </OTH_INFO_PRIOR_INFORMATION>
                </FD_PRIOR_INFORMATION_DEFENCE>
            </PRIOR_INFORMATION_DEFENCE>
        </FORM_SECTION>
    </TED_EXPORT>
    """
    result = parse_notice_dispatch_date(xml_content)
    assert result == "2020-07-30T00:00:00+00:00"


def test_parse_notice_dispatch_date_invalid_format():
    """Test parsing dispatch date with invalid format."""
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <TED_EXPORT>
        <FORM_SECTION>
            <F02_2014>
                <COMPLEMENTARY_INFO>
                    <DATE_DISPATCH_NOTICE>invalid-date</DATE_DISPATCH_NOTICE>
                </COMPLEMENTARY_INFO>
            </F02_2014>
        </FORM_SECTION>
    </TED_EXPORT>
    """
    result = parse_notice_dispatch_date(xml_content)
    assert result is None


def test_parse_notice_dispatch_date_not_found():
    """Test parsing when dispatch date is not found."""
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <TED_EXPORT>
        <FORM_SECTION>
            <F02_2014>
                <COMPLEMENTARY_INFO>
                    <!-- No DATE_DISPATCH_NOTICE element -->
                </COMPLEMENTARY_INFO>
            </F02_2014>
        </FORM_SECTION>
    </TED_EXPORT>
    """
    result = parse_notice_dispatch_date(xml_content)
    assert result is None


def test_parse_notice_dispatch_date_invalid_xml():
    """Test parsing with invalid XML."""
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <TED_EXPORT>
        <FORM_SECTION>
            <F02_2014>
                <COMPLEMENTARY_INFO>
                    <DATE_DISPATCH_NOTICE>2020-05-15</DATE_DISPATCH_NOTICE>
                </COMPLEMENTARY_INFO>
            <!-- Missing closing tag -->
        </FORM_SECTION>
    </TED_EXPORT>
    """
    with pytest.raises(etree.XMLSyntaxError):
        parse_notice_dispatch_date(xml_content)


def run_main_and_get_result(xml_file, output_dir):
    """Run main conversion and return the result."""
    main(str(xml_file), str(output_dir), "ocds-test-prefix", "test-scheme")
    output_files = list(output_dir.glob("*_release_0.json"))
    assert len(output_files) == 1, f"Expected 1 output file, got {len(output_files)}"
    with output_files[0].open() as f:
        return json.load(f)


def test_ted_bt_05_integration(tmp_path, temp_output_dir):
    """Integration test for TED BT-05 conversion."""
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <TED_EXPORT>
        <FORM_SECTION>
            <F02_2014>
                <COMPLEMENTARY_INFO>
                    <DATE_DISPATCH_NOTICE>2020-05-15</DATE_DISPATCH_NOTICE>
                </COMPLEMENTARY_INFO>
            </F02_2014>
        </FORM_SECTION>
    </TED_EXPORT>
    """
    
    # Create input XML file
    xml_file = tmp_path / "test_input_ted_notice_dispatch_date.xml"
    xml_file.write_text(xml_content)
    
    # Run main and get result
    result = run_main_and_get_result(xml_file, temp_output_dir)
    
    # Verify the result
    assert "date" in result
    assert result["date"] == "2020-05-15T00:00:00+00:00"


if __name__ == "__main__":
    pytest.main(["-v"])
