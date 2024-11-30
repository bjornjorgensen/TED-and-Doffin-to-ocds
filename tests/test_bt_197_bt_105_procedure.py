import json
import sys
import tempfile
from pathlib import Path

import pytest

# Add the parent directory to sys.path to import main
sys.path.append(str(Path(__file__).parent.parent))
from src.ted_and_doffin_to_ocds.main import main


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


def test_bt_197_bt_105_procedure_integration(tmp_path, temp_output_dir) -> None:
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
                    <cbc:ReasonCode listName="non-publication-justification">oth-int</cbc:ReasonCode>
                  </efac:FieldsPrivacy>
                </efext:EformsExtension>
              </ext:ExtensionContent>
            </ext:UBLExtension>
          </ext:UBLExtensions>
        </cac:TenderingProcess>
    </ContractNotice>
    """
    xml_file = tmp_path / "test_input_unpublished_justification_code.xml"
    xml_file.write_text(xml_content)

    result = run_main_and_get_result(xml_file, temp_output_dir)

    assert "withheldInformation" in result, "Expected 'withheldInformation' in result"
    assert (
        len(result["withheldInformation"]) == 1
    ), f"Expected 1 withheld information item, got {len(result['withheldInformation'])}"

    withheld_info = result["withheldInformation"][0]
    assert (
        withheld_info["field"] == "pro-typ"
    ), f"Expected field 'pro-typ', got {withheld_info['field']}"
    assert (
        "rationaleClassifications" in withheld_info
    ), "Expected 'rationaleClassifications' in withheld_info"
    assert (
        len(withheld_info["rationaleClassifications"]) == 1
    ), f"Expected 1 rationale classification, got {len(withheld_info['rationaleClassifications'])}"

    classification = withheld_info["rationaleClassifications"][0]
    assert (
        classification["scheme"] == "eu-non-publication-justification"
    ), f"Expected scheme 'eu-non-publication-justification', got {classification['scheme']}"
    assert (
        classification["id"] == "oth-int"
    ), f"Expected id 'oth-int', got {classification['id']}"
    assert (
        classification["description"] == "Other public interest"
    ), f"Expected description 'Other public interest', got {classification['description']}"
    assert (
        classification["uri"]
        == "http://publications.europa.eu/resource/authority/non-publication-justification/oth-int"
    ), f"Unexpected URI: {classification['uri']}"


if __name__ == "__main__":
    pytest.main(["-v", "-s"])
