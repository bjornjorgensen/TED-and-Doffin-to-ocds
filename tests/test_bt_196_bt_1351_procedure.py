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


def test_bt_196_bt_1351_procedure_integration(tmp_path, temp_output_dir) -> None:
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractNotice xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
        xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
        xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
        xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
        xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
        xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1">
        <cac:TenderingProcess>
          <cac:ProcessJustification>
            <cbc:ProcessReasonCode listName="accelerated-procedure">some-code</cbc:ProcessReasonCode>
            <ext:UBLExtensions>
              <ext:UBLExtension>
                <ext:ExtensionContent>
                  <efext:EformsExtension>
                    <efac:FieldsPrivacy>
                      <efbc:FieldIdentifierCode>pro-acc-jus</efbc:FieldIdentifierCode>
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
    xml_file = tmp_path / "test_input_unpublished_justification_bt1351.xml"
    xml_file.write_text(xml_content)

    result = run_main_and_get_result(xml_file, temp_output_dir)

    assert "withheldInformation" in result, "Expected 'withheldInformation' in result"
    assert (
        len(result["withheldInformation"]) == 1
    ), f"Expected 1 withheld information item, got {len(result['withheldInformation'])}"

    withheld_info = result["withheldInformation"][0]
    assert (
        withheld_info["id"] == "pro-acc-jus"
    ), f"Expected id 'pro-acc-jus', got {withheld_info.get('id')}"
    
    assert "rationale" in withheld_info, "Expected 'rationale' in withheld_info"
    assert isinstance(withheld_info["rationale"], dict), "Rationale should be a dictionary"
    
    rationale = withheld_info["rationale"]
    assert "text" in rationale, "Expected 'text' in rationale"
    assert (
        rationale["text"] == "Information delayed publication because of ..."
    ), f"Unexpected rationale text: {rationale.get('text')}"
    
    assert "language" in rationale, "Expected 'language' in rationale"
    assert (
        rationale["language"] == "ENG"
    ), f"Unexpected language: {rationale.get('language')}"


if __name__ == "__main__":
    pytest.main(["-v", "-s"])
