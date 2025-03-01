import json
import logging
import sys
import tempfile
from pathlib import Path

import pytest

# Add the parent directory to sys.path to import main
sys.path.append(str(Path(__file__).parent.parent))
from src.ted_and_doffin_to_ocds.main import configure_logging, main
from src.ted_and_doffin_to_ocds.converters.eforms.bt_196_bt_105_procedure import parse_bt196_bt105_unpublished_justification


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
    logger = logging.getLogger(__name__)
    # logger.info("Running main function") # Logging disabled
    main(str(xml_file), str(output_dir), "ocds-test-prefix", "test-scheme")
    # logger.info("Main function executed") # Logging disabled
    output_files = list(output_dir.glob("*.json"))
    # logger.info("Output files: %s", output_files) # Logging disabled
    #if not output_files:
        # logger.error("No output files found") # Logging disabled
    assert len(output_files) == 1, f"Expected 1 output file, got {len(output_files)}"
    with output_files[0].open() as f:
        return json.load(f)


def test_bt_196_bt_105_procedure_integration(
    tmp_path, setup_logging, temp_output_dir
) -> None:
    logger = setup_logging

    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractNotice xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
        xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
        xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
        xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
        xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
        xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1">
        <cac:TenderingProcess>
          <ext:UBLExtensions>
            <ext:UBLExtension>
              <ext:ExtensionContent>
                <efext:EformsExtension>
                  <efac:FieldsPrivacy>
                    <efbc:FieldIdentifierCode>pro-typ</efbc:FieldIdentifierCode>
                    <efbc:ReasonDescription languageID="ENG">Information delayed publication because of ...</efbc:ReasonDescription>
                  </efac:FieldsPrivacy>
                </efext:EformsExtension>
              </ext:ExtensionContent>
            </ext:UBLExtension>
          </ext:UBLExtensions>
        </cac:TenderingProcess>
    </ContractNotice>
    """
    xml_file = tmp_path / "test_input_unpublished_justification.xml"
    xml_file.write_text(xml_content)
    # logger.info("Created XML file at %s", xml_file) # Logging disabled
    # logger.info("Output directory: %s", temp_output_dir) # Logging disabled

    result = run_main_and_get_result(xml_file, temp_output_dir)
    # logger.info("Result: %s", json.dumps(result, indent=2) # Logging disabled)

    assert "withheldInformation" in result, "Expected 'withheldInformation' in result"
    assert (
        len(result["withheldInformation"]) == 1
    ), f"Expected 1 withheld information item, got {len(result['withheldInformation'])}"

    withheld_info = result["withheldInformation"][0]
    assert (
        withheld_info["field"] == "pro-typ"
    ), f"Expected field 'pro-typ', got {withheld_info['field']}"
    assert "rationale" in withheld_info, "Expected 'rationale' in withheld_info"
    
    # Updated assertion to handle both string and dictionary rationales
    if isinstance(withheld_info["rationale"], dict):
        assert "ENG" in withheld_info["rationale"], "Expected 'ENG' language in rationale"
        assert (
            withheld_info["rationale"]["ENG"] == "Information delayed publication because of ..."
        ), f"Expected ENG rationale 'Information delayed publication because of ...', got {withheld_info['rationale']['ENG']}"
    else:
        assert (
            withheld_info["rationale"] == "Information delayed publication because of ..."
        ), f"Expected rationale 'Information delayed publication because of ...', got {withheld_info['rationale']}"


def test_multilingual_rationale(setup_logging):
    """Test parsing of multilingual rationales."""
    logger = setup_logging

    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractNotice xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
        xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
        xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
        xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
        xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
        xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1">
        <cac:TenderingProcess>
          <ext:UBLExtensions>
            <ext:UBLExtension>
              <ext:ExtensionContent>
                <efext:EformsExtension>
                  <efac:FieldsPrivacy>
                    <efbc:FieldIdentifierCode>pro-typ</efbc:FieldIdentifierCode>
                    <efbc:ReasonDescription languageID="ENG">Information delayed publication because of security</efbc:ReasonDescription>
                    <efbc:ReasonDescription languageID="NOR">Informasjon forsinket publisering på grunn av sikkerhet</efbc:ReasonDescription>
                  </efac:FieldsPrivacy>
                </efext:EformsExtension>
              </ext:ExtensionContent>
            </ext:UBLExtension>
          </ext:UBLExtensions>
        </cac:TenderingProcess>
    </ContractNotice>
    """
    
    result = parse_bt196_bt105_unpublished_justification(xml_content)
    
    assert result is not None
    assert "withheldInformation" in result
    assert len(result["withheldInformation"]) == 1
    
    withheld_info = result["withheldInformation"][0]
    assert withheld_info["field"] == "pro-typ"
    assert isinstance(withheld_info["rationale"], dict)
    assert "ENG" in withheld_info["rationale"]
    assert "NOR" in withheld_info["rationale"]
    assert withheld_info["rationale"]["ENG"] == "Information delayed publication because of security"
    assert withheld_info["rationale"]["NOR"] == "Informasjon forsinket publisering på grunn av sikkerhet"

def test_single_rationale_no_language(setup_logging):
    """Test parsing of a single rationale without language attribute."""
    logger = setup_logging

    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractNotice xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
        xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
        xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
        xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
        xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
        xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1">
        <cac:TenderingProcess>
          <ext:UBLExtensions>
            <ext:UBLExtension>
              <ext:ExtensionContent>
                <efext:EformsExtension>
                  <efac:FieldsPrivacy>
                    <efbc:FieldIdentifierCode>pro-typ</efbc:FieldIdentifierCode>
                    <efbc:ReasonDescription>Information delayed publication no language attribute</efbc:ReasonDescription>
                  </efac:FieldsPrivacy>
                </efext:EformsExtension>
              </ext:ExtensionContent>
            </ext:UBLExtension>
          </ext:UBLExtensions>
        </cac:TenderingProcess>
    </ContractNotice>
    """
    
    result = parse_bt196_bt105_unpublished_justification(xml_content)
    
    assert result is not None
    assert "withheldInformation" in result
    assert len(result["withheldInformation"]) == 1
    
    withheld_info = result["withheldInformation"][0]
    assert withheld_info["field"] == "pro-typ"
    assert isinstance(withheld_info["rationale"], str)
    assert withheld_info["rationale"] == "Information delayed publication no language attribute"

def test_mixed_rationales(setup_logging):
    """Test parsing with both languageID and non-languageID elements."""
    logger = setup_logging

    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractNotice xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
        xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
        xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
        xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
        xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
        xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1">
        <cac:TenderingProcess>
          <ext:UBLExtensions>
            <ext:UBLExtension>
              <ext:ExtensionContent>
                <efext:EformsExtension>
                  <efac:FieldsPrivacy>
                    <efbc:FieldIdentifierCode>pro-typ</efbc:FieldIdentifierCode>
                    <efbc:ReasonDescription languageID="ENG">English rationale</efbc:ReasonDescription>
                    <efbc:ReasonDescription>Default rationale</efbc:ReasonDescription>
                  </efac:FieldsPrivacy>
                </efext:EformsExtension>
              </ext:ExtensionContent>
            </ext:UBLExtension>
          </ext:UBLExtensions>
        </cac:TenderingProcess>
    </ContractNotice>
    """
    
    # In this case, we should prioritize the language-specific entries
    result = parse_bt196_bt105_unpublished_justification(xml_content)
    
    assert result is not None
    assert "withheldInformation" in result
    withheld_info = result["withheldInformation"][0]
    
    # We should have a dictionary with the language entry,
    # but the non-language entry should be ignored if we have language entries
    assert isinstance(withheld_info["rationale"], dict)
    assert "ENG" in withheld_info["rationale"]
    assert withheld_info["rationale"]["ENG"] == "English rationale"

if __name__ == "__main__":
    pytest.main(["-v", "-s"])
