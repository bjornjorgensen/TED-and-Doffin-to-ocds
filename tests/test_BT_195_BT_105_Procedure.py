# tests/test_BT_195_BT_105_Procedure.py

import pytest
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main

def test_bt_195_bt_105_unpublished_procedure_type_integration(tmp_path):
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
            <ext:UBLExtensions>
              <ext:UBLExtension>
                <ext:ExtensionContent>
                  <efext:EformsExtension>
                    <efac:FieldsPrivacy>
                      <efbc:FieldIdentifierCode listName="non-publication-identifier">pro-typ</efbc:FieldIdentifierCode>
                      <efbc:ReasonDescription languageID="ENG">Information delayed publication because of ...</efbc:ReasonDescription>
                      <cbc:ReasonCode listName="non-publication-justification">oth-int</cbc:ReasonCode>
                      <efbc:PublicationDate>2025-03-31+01:00</efbc:PublicationDate>
                    </efac:FieldsPrivacy>
                  </efext:EformsExtension>
                </ext:ExtensionContent>
              </ext:UBLExtension>
            </ext:UBLExtensions>
          </cac:ProcessJustification>
        </cac:TenderingProcess>
    </root>
    """
    xml_file = tmp_path / "test_input_unpublished_procedure_type.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open('output.json', 'r') as f:
        result = json.load(f)

    assert "withheldInformation" in result, "Expected 'withheldInformation' in result"
    assert len(result["withheldInformation"]) == 1, f"Expected 1 withheld information item, got {len(result['withheldInformation'])}"

    withheld_info = result["withheldInformation"][0]
    assert withheld_info["id"] == "pro-typ-18d27a53-0109-4f93-9231-6659d931bce0", f"Expected id 'pro-typ-18d27a53-0109-4f93-9231-6659d931bce0', got {withheld_info['id']}"
    assert withheld_info["field"] == "pro-typ", f"Expected field 'pro-typ', got {withheld_info['field']}"
    assert withheld_info["name"] == "Procedure Type", f"Expected name 'Procedure Type', got {withheld_info['name']}"
    assert withheld_info["rationale"] == "Information delayed publication because of ...", f"Expected rationale 'Information delayed publication because of ...', got {withheld_info.get('rationale')}"
    
    assert "rationaleClassifications" in withheld_info, "Expected 'rationaleClassifications' in withheld_info"
    assert len(withheld_info["rationaleClassifications"]) == 1, f"Expected 1 rationale classification, got {len(withheld_info['rationaleClassifications'])}"
    
    rationale_classification = withheld_info["rationaleClassifications"][0]
    assert rationale_classification["scheme"] == "eu-non-publication-justification", f"Expected scheme 'eu-non-publication-justification', got {rationale_classification['scheme']}"
    assert rationale_classification["id"] == "oth-int", f"Expected id 'oth-int', got {rationale_classification['id']}"
    assert rationale_classification["description"] == "Other public interest", f"Expected description 'Other public interest', got {rationale_classification['description']}"
    assert rationale_classification["uri"] == "http://publications.europa.eu/resource/authority/non-publication-justification/oth-int", f"Expected URI 'http://publications.europa.eu/resource/authority/non-publication-justification/oth-int', got {rationale_classification['uri']}"

    assert withheld_info["availabilityDate"] == "2025-03-31T00:00:00+01:00", f"Expected availabilityDate '2025-03-31T00:00:00+01:00', got {withheld_info.get('availabilityDate')}"

if __name__ == "__main__":
    pytest.main()