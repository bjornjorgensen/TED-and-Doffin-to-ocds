import json
import logging
import sys
import tempfile
from pathlib import Path
import xml.etree.ElementTree as ET
from lxml import etree

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


def test_bt196_bt553_tender_missing_data(
    tmp_path, setup_logging, temp_output_dir
) -> None:
    logger = setup_logging
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractNotice xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
        xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
        xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
        xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
        xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
        xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1">
        <ext:UBLExtensions>
            <ext:UBLExtension>
                <ext:ExtensionContent>
                    <efext:EformsExtension>
                        <efac:NoticeResult>
                            <efac:LotTender>
                                <!-- Missing SubcontractingTerm element -->
                            </efac:LotTender>
                        </efac:NoticeResult>
                    </efext:EformsExtension>
                </ext:ExtensionContent>
            </ext:UBLExtension>
        </ext:UBLExtensions>
    </ContractNotice>
    """
    xml_file = tmp_path / "test_input_bt196_bt553_tender_missing.xml"
    xml_file.write_text(xml_content)

    result = run_main_and_get_result(xml_file, temp_output_dir)

    # logger.info("Result: %s", json.dumps(result, indent=2) # Logging disabled)

    assert (
        "withheldInformation" not in result
    ), "Did not expect 'withheldInformation' in result when data is missing"


def test_bt196_bt553_xpath_validation(tmp_path, setup_logging) -> None:
    logger = setup_logging
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractNotice xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
        xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
        xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
        xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
        xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
        xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1">
        <ext:UBLExtensions>
            <ext:UBLExtension>
                <ext:ExtensionContent>
                    <efext:EformsExtension>
                        <efac:NoticeResult>
                            <efac:LotTender>
                                <efac:SubcontractingTerm>
                                    <efbc:TermCode listName="applicability"/>
                                    <efac:FieldsPrivacy>
                                        <efbc:FieldIdentifierCode>sub-val</efbc:FieldIdentifierCode>
                                        <efbc:ReasonDescription>Information delayed publication because of ...</efbc:ReasonDescription>
                                    </efac:FieldsPrivacy>
                                </efac:SubcontractingTerm>
                            </efac:LotTender>
                        </efac:NoticeResult>
                    </efext:EformsExtension>
                </ext:ExtensionContent>
            </ext:UBLExtension>
        </ext:UBLExtensions>
    </ContractNotice>
    """
    xml_file = tmp_path / "test_xpath_validation.xml"
    xml_file.write_text(xml_content)
    
    # Parse the XML
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
        'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
        'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
        'efbc': 'http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1'
    }
    
    tree = etree.parse(str(xml_file))
    root = tree.getroot()
    
    # XPath for the ReasonDescription
    xpath = "/*/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:NoticeResult/efac:LotTender/efac:SubcontractingTerm[efbc:TermCode/@listName='applicability']/efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='sub-val']/efbc:ReasonDescription"
    
    # Find the element using XPath
    reason_elements = root.xpath(xpath, namespaces=namespaces)
    
    # Verify we found exactly one element
    assert len(reason_elements) == 1, f"Expected 1 element matching XPath, got {len(reason_elements)}"
    
    # Verify the element's text
    reason_text = reason_elements[0].text
    assert reason_text == "Information delayed publication because of ...", f"Unexpected reason text: {reason_text}"


if __name__ == "__main__":
    pytest.main(["-v", "-s"])
