# tests/test_bt_195_bt_1351_procedure.py
from pathlib import Path
import pytest
import json
import sys

# Add the parent directory to sys.path to import main
sys.path.append(str(Path(__file__).parent.parent))
from src.ted_and_doffin_to_ocds.main import main


def test_bt_195_bt_1351_procedure_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
          xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
          xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1">
        <cbc:ContractFolderID>18d27a53-0109-4f93-9231-6659d931bce0</cbc:ContractFolderID>
        <cac:TenderingProcess>
          <cac:ProcessJustification>
            <cbc:ProcessReasonCode listName="accelerated-procedure">some-code</cbc:ProcessReasonCode>
            <ext:UBLExtensions>
              <ext:UBLExtension>
                <ext:ExtensionContent>
                  <efext:EformsExtension>
                    <efac:FieldsPrivacy>
                      <efbc:FieldIdentifierCode>pro-acc-jus</efbc:FieldIdentifierCode>
                    </efac:FieldsPrivacy>
                  </efext:EformsExtension>
                </ext:ExtensionContent>
              </ext:UBLExtension>
            </ext:UBLExtensions>
          </cac:ProcessJustification>
        </cac:TenderingProcess>
    </root>
    """
    xml_file = tmp_path / "test_input_unpublished_identifier_bt1351.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with Path("output.json").open() as f:
        result = json.load(f)

    assert "withheldInformation" in result, "Expected 'withheldInformation' in result"
    assert (
        len(result["withheldInformation"]) == 1
    ), f"Expected 1 withheld information item, got {len(result['withheldInformation'])}"

    withheld_info = result["withheldInformation"][0]
    assert (
        withheld_info["id"] == "pro-acc-jus-18d27a53-0109-4f93-9231-6659d931bce0"
    ), f"Expected id 'pro-acc-jus-18d27a53-0109-4f93-9231-6659d931bce0', got {withheld_info['id']}"
    assert (
        withheld_info["field"] == "pro-acc-jus"
    ), f"Expected field 'pro-acc-jus', got {withheld_info['field']}"
    assert (
        withheld_info["name"] == "procedure Accelerated Justification"
    ), f"Expected name 'procedure Accelerated Justification', got {withheld_info['name']}"


if __name__ == "__main__":
    pytest.main()
