# tests/test_BT_196_BT_09_Procedure.py

import pytest
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main


def test_bt_196_bt_09_procedure_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
          xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
          xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1">
        <cbc:ContractFolderID>test-folder-id</cbc:ContractFolderID>
        <cac:TenderingTerms>
            <cac:ProcurementLegislationDocumentReference>
                <cbc:ID>CrossBorderLaw</cbc:ID>
                <ext:UBLExtensions>
                    <ext:UBLExtension>
                        <ext:ExtensionContent>
                            <efext:EformsExtension>
                                <efac:FieldsPrivacy>
                                    <efbc:FieldIdentifierCode>cro-bor-law</efbc:FieldIdentifierCode>
                                    <efbc:ReasonDescription>Information delayed publication because of ...</efbc:ReasonDescription>
                                </efac:FieldsPrivacy>
                            </efext:EformsExtension>
                        </ext:ExtensionContent>
                    </ext:UBLExtension>
                </ext:UBLExtensions>
            </cac:ProcurementLegislationDocumentReference>
        </cac:TenderingTerms>
    </root>
    """
    xml_file = tmp_path / "test_input_unpublished_justification.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open("output.json") as f:
        result = json.load(f)

    assert "withheldInformation" in result, "Expected 'withheldInformation' in result"
    assert (
        len(result["withheldInformation"]) == 1
    ), f"Expected 1 withheld information item, got {len(result['withheldInformation'])}"

    withheld_item = result["withheldInformation"][0]
    assert (
        "rationale" in withheld_item
    ), "Expected 'rationale' in withheld information item"
    assert (
        withheld_item["rationale"] == "Information delayed publication because of ..."
    ), f"Expected rationale 'Information delayed publication because of ...', got {withheld_item['rationale']}"


if __name__ == "__main__":
    pytest.main()
