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
    logger = logging.getLogger(__name__)
    logger.info("Running main function")
    main(str(xml_file), str(output_dir), "ocds-test-prefix", "test-scheme")
    logger.info("Main function executed")
    output_files = list(output_dir.glob("*.json"))
    logger.info("Output files: %s", output_files)
    if not output_files:
        logger.error("No output files found")
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
          <cac:ProcessJustification>
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
          </cac:ProcessJustification>
        </cac:TenderingProcess>
    </ContractNotice>
    """
    xml_file = tmp_path / "test_input_unpublished_justification.xml"
    xml_file.write_text(xml_content)
    logger.info("Created XML file at %s", xml_file)
    logger.info("Output directory: %s", temp_output_dir)

    result = run_main_and_get_result(xml_file, temp_output_dir)
    logger.info("Result: %s", json.dumps(result, indent=2))

    assert "withheldInformation" in result, "Expected 'withheldInformation' in result"
    assert (
        len(result["withheldInformation"]) == 1
    ), f"Expected 1 withheld information item, got {len(result['withheldInformation'])}"

    withheld_info = result["withheldInformation"][0]
    assert (
        withheld_info["field"] == "pro-typ"
    ), f"Expected field 'pro-typ', got {withheld_info['field']}"
    assert "rationale" in withheld_info, "Expected 'rationale' in withheld_info"
    assert (
        withheld_info["rationale"] == "Information delayed publication because of ..."
    ), f"Expected rationale 'Information delayed publication because of ...', got {withheld_info['rationale']}"


if __name__ == "__main__":
    pytest.main(["-v", "-s"])
