import json
import logging
import sys
import tempfile
from pathlib import Path

import pytest
from lxml import etree

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
    output_files = list(output_dir.glob("*_release_*.json"))
    if not output_files:
        raise FileNotFoundError("No output files generated")
    # Return the most recent file if multiple exist
    latest_file = max(output_files, key=lambda p: p.stat().st_mtime)
    with latest_file.open() as f:
        return json.load(f)


def test_bt195_bt162_unpublished_identifier_integration(
    tmp_path, setup_logging, temp_output_dir
) -> None:
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractNotice-2"
    xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
    xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
    xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
    xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
    xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
    xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1">
    <ext:UBLExtensions>
        <ext:UBLExtension>
            <ext:ExtensionContent>
                <efext:EformsExtension>
                    <efac:NoticeResult>
                        <efac:LotTender>
                            <cbc:ID schemeName="result">TEN-0001</cbc:ID>
                            <efac:ConcessionRevenue>
                                <efac:FieldsPrivacy>
                                    <efbc:FieldIdentifierCode listName="non-publication-identifier">con-rev-use</efbc:FieldIdentifierCode>
                                </efac:FieldsPrivacy>
                            </efac:ConcessionRevenue>
                        </efac:LotTender>
                    </efac:NoticeResult>
                </efext:EformsExtension>  
            </ext:ExtensionContent>
        </ext:UBLExtension>
    </ext:UBLExtensions>
    </ContractNotice>"""

    xml_file = tmp_path / "test_input_bt195_bt162.xml"
    xml_file.write_text(xml_content)

    result = run_main_and_get_result(xml_file, temp_output_dir)

    # logger.info("Result: %s", json.dumps(result, indent=2) # Logging disabled)

    assert "withheldInformation" in result, "Expected 'withheldInformation' in result"
    assert (
        len(result["withheldInformation"]) == 1
    ), "Expected one withheld information item"

    withheld_item = result["withheldInformation"][0]
    assert (
        withheld_item["id"] == "con-rev-use-TEN-0001"
    ), "Unexpected withheld information id"
    assert (
        withheld_item["field"] == "con-rev-use"
    ), "Unexpected withheld information field"
    assert (
        withheld_item["name"] == "Concession Revenue User"
    ), "Unexpected withheld information name"


def test_bt195_bt162_unpublished_identifier_missing_data(
    tmp_path, setup_logging, temp_output_dir
) -> None:
    logger = setup_logging
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractNotice-2"
    xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
    xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
    xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
    xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
    xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
    xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1">
    <ext:UBLExtensions>
        <ext:UBLExtension>
            <ext:ExtensionContent>
                <efext:EformsExtension>
                    <efac:NoticeResult>
                        <efac:LotTender>
                            <cbc:ID schemeName="result">TEN-0001</cbc:ID>
                            <efac:ConcessionRevenue>
                                <!-- Missing FieldsPrivacy element -->
                            </efac:ConcessionRevenue>
                        </efac:LotTender>
                    </efac:NoticeResult>
                </efext:EformsExtension>  
            </ext:ExtensionContent>
        </ext:UBLExtension>
    </ext:UBLExtensions>
    </ContractNotice>"""

    xml_file = tmp_path / "test_input_bt195_bt162_missing.xml"
    xml_file.write_text(xml_content)

    result = run_main_and_get_result(xml_file, temp_output_dir)

    # logger.info("Result: %s", json.dumps(result, indent=2) # Logging disabled)

    assert (
        "withheldInformation" not in result
    ), "Did not expect 'withheldInformation' in result when data is missing"


def test_bt195_bt162_multiple_withheld_items(tmp_path, setup_logging, temp_output_dir) -> None:
    logger = setup_logging
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractNotice-2"
    xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
    xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
    xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
    xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
    xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
    xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1">
    <ext:UBLExtensions>
        <ext:UBLExtension>
            <ext:ExtensionContent>
                <efext:EformsExtension>
                    <efac:NoticeResult>
                        <efac:LotTender>
                            <cbc:ID schemeName="result">TEN-0001</cbc:ID>
                            <efac:ConcessionRevenue>
                                <efac:FieldsPrivacy>
                                    <efbc:FieldIdentifierCode listName="non-publication-identifier">con-rev-use</efbc:FieldIdentifierCode>
                                </efac:FieldsPrivacy>
                            </efac:ConcessionRevenue>
                        </efac:LotTender>
                        <efac:LotTender>
                            <cbc:ID schemeName="result">TEN-0002</cbc:ID>
                            <efac:ConcessionRevenue>
                                <efac:FieldsPrivacy>
                                    <efbc:FieldIdentifierCode listName="non-publication-identifier">con-rev-use</efbc:FieldIdentifierCode>
                                </efac:FieldsPrivacy>
                            </efac:ConcessionRevenue>
                        </efac:LotTender>
                    </efac:NoticeResult>
                </efext:EformsExtension>  
            </ext:ExtensionContent>
        </ext:UBLExtension>
    </ext:UBLExtensions>
    </ContractNotice>"""

    xml_file = tmp_path / "test_input_bt195_bt162_multiple.xml"
    xml_file.write_text(xml_content)

    result = run_main_and_get_result(xml_file, temp_output_dir)

    assert "withheldInformation" in result
    assert len(result["withheldInformation"]) == 2

    # Check first item
    assert result["withheldInformation"][0]["id"] == "con-rev-use-TEN-0001"
    assert result["withheldInformation"][0]["field"] == "con-rev-use"
    assert result["withheldInformation"][0]["name"] == "Concession Revenue User"

    # Check second item
    assert result["withheldInformation"][1]["id"] == "con-rev-use-TEN-0002"
    assert result["withheldInformation"][1]["field"] == "con-rev-use"
    assert result["withheldInformation"][1]["name"] == "Concession Revenue User"

def test_bt195_bt162_malformed_xml(tmp_path, setup_logging, temp_output_dir) -> None:
    logger = setup_logging
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractNotice>
        <invalid>
            <not-closed>
        </invalid>
    """  # No closing ContractNotice tag and invalid nesting

    xml_file = tmp_path / "test_input_bt195_bt162_malformed.xml"
    xml_file.write_text(xml_content)

    with pytest.raises((etree.XMLSyntaxError, Exception)):
        # Try to parse the XML directly to verify it's actually malformed
        etree.fromstring(xml_content)

def test_bt195_bt162_string_bytes_input(tmp_path, setup_logging, temp_output_dir) -> None:
    logger = setup_logging
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractNotice-2"
    xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
    xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
    xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
    xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
    xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
    xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1">
    <ext:UBLExtensions>
        <ext:UBLExtension>
            <ext:ExtensionContent>
                <efext:EformsExtension>
                    <efac:NoticeResult>
                        <efac:LotTender>
                            <cbc:ID schemeName="result">TEN-0001</cbc:ID>
                            <efac:ConcessionRevenue>
                                <efac:FieldsPrivacy>
                                    <efbc:FieldIdentifierCode listName="non-publication-identifier">con-rev-use</efbc:FieldIdentifierCode>
                                </efac:FieldsPrivacy>
                            </efac:ConcessionRevenue>
                        </efac:LotTender>
                    </efac:NoticeResult>
                </efext:EformsExtension>  
            </ext:ExtensionContent>
        </ext:UBLExtension>
    </ext:UBLExtensions>
    </ContractNotice>"""

    # Test with string input
    xml_file = tmp_path / "test_input_bt195_bt162_string.xml"
    xml_file.write_text(xml_content)
    result_string = run_main_and_get_result(xml_file, temp_output_dir)

    # Test with bytes input
    xml_file = tmp_path / "test_input_bt195_bt162_bytes.xml"
    xml_file.write_bytes(xml_content.encode('utf-8'))
    result_bytes = run_main_and_get_result(xml_file, temp_output_dir)

    # Compare everything except dynamic fields like ocid
    assert {k: v for k, v in result_string.items() if k != 'ocid'} == \
           {k: v for k, v in result_bytes.items() if k != 'ocid'}
    assert "withheldInformation" in result_string
    assert len(result_string["withheldInformation"]) == 1
    assert result_string["withheldInformation"] == result_bytes["withheldInformation"]


if __name__ == "__main__":
    pytest.main(["-v", "-s"])
