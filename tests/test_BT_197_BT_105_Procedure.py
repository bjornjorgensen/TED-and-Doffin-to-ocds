# tests/test_BT_197_BT_105_Procedure.py

import pytest
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main

def test_bt_197_bt_105_procedure_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
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
    </root>
    """
    xml_file = tmp_path / "test_input_unpublished_justification_code.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open('output.json', 'r') as f:
        result = json.load(f)

    assert "withheldInformation" in result, "Expected 'withheldInformation' in result"
    assert len(result["withheldInformation"]) == 1, f"Expected 1 withheld information item, got {len(result['withheldInformation'])}"

    withheld_info = result["withheldInformation"][0]
    assert withheld_info["field"] == "pro-typ", f"Expected field 'pro-typ', got {withheld_info['field']}"
    assert "rationaleClassifications" in withheld_info, "Expected 'rationaleClassifications' in withheld_info"
    assert len(withheld_info["rationaleClassifications"]) == 1, f"Expected 1 rationale classification, got {len(withheld_info['rationaleClassifications'])}"

    classification = withheld_info["rationaleClassifications"][0]
    assert classification["scheme"] == "eu-non-publication-justification", f"Expected scheme 'eu-non-publication-justification', got {classification['scheme']}"
    assert classification["id"] == "oth-int", f"Expected id 'oth-int', got {classification['id']}"
    assert classification["description"] == "Other public interest", f"Expected description 'Other public interest', got {classification['description']}"
    assert classification["uri"] == "http://publications.europa.eu/resource/authority/non-publication-justification/oth-int", f"Unexpected URI: {classification['uri']}"

if __name__ == "__main__":
    pytest.main()