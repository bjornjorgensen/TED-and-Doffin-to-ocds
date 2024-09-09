# tests/test_BT_195_BT_1252_Procedure.py

import pytest
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main


def test_bt_195_bt_1252_procedure_integration(tmp_path):
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
            <cbc:ProcessReasonCode listName="direct-award-justification">some-code</cbc:ProcessReasonCode>
            <ext:UBLExtensions>
              <ext:UBLExtension>
                <ext:ExtensionContent>
                  <efext:EformsExtension>
                    <efac:FieldsPrivacy>
                      <efbc:FieldIdentifierCode>dir-awa-pre</efbc:FieldIdentifierCode>
                    </efac:FieldsPrivacy>
                  </efext:EformsExtension>
                </ext:ExtensionContent>
              </ext:UBLExtension>
            </ext:UBLExtensions>
          </cac:ProcessJustification>
        </cac:TenderingProcess>
    </root>
    """
    xml_file = tmp_path / "test_input_unpublished_identifier_bt1252.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open("output.json") as f:
        result = json.load(f)

    assert "withheldInformation" in result, "Expected 'withheldInformation' in result"
    assert (
        len(result["withheldInformation"]) == 1
    ), f"Expected 1 withheld information item, got {len(result['withheldInformation'])}"

    withheld_info = result["withheldInformation"][0]
    assert (
        withheld_info["id"] == "dir-awa-pre-18d27a53-0109-4f93-9231-6659d931bce0"
    ), f"Expected id 'dir-awa-pre-18d27a53-0109-4f93-9231-6659d931bce0', got {withheld_info['id']}"
    assert (
        withheld_info["field"] == "dir-awa-pre"
    ), f"Expected field 'dir-awa-pre', got {withheld_info['field']}"
    assert (
        withheld_info["name"]
        == "Direct Award Justification Previous Procedure Identifier"
    ), f"Expected name 'Direct Award Justification Previous Procedure Identifier', got {withheld_info['name']}"


if __name__ == "__main__":
    pytest.main()
