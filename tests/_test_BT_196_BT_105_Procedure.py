# tests/test_BT_196_BT_105_Procedure.py

import pytest
import json
import os
import sys
import logging

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main
from converters.BT_196_BT_105_Procedure import parse_unpublished_justification_description_procedure_bt105, merge_unpublished_justification_description_procedure_bt105

logger = logging.getLogger(__name__)

def test_parse_unpublished_justification_description_procedure_bt105():
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
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
                                <efbc:ReasonDescription>Information delayed publication because of sensitive procedure type</efbc:ReasonDescription>
                            </efac:FieldsPrivacy>
                        </efext:EformsExtension>
                    </ext:ExtensionContent>
                </ext:UBLExtension>
            </ext:UBLExtensions>
        </cac:TenderingProcess>
    </root>
    """
    
    result = parse_unpublished_justification_description_procedure_bt105(xml_content)
    assert result == "Information delayed publication because of sensitive procedure type"

def test_merge_unpublished_justification_description_procedure_bt105():
    release_json = {
        "withheldInformation": [
            {
                "id": "pro-typ-1234",
                "field": "pro-typ",
                "name": "Procedure Type"
            }
        ]
    }
    
    rationale = "Information delayed publication because of sensitive procedure type"
    
    merge_unpublished_justification_description_procedure_bt105(release_json, rationale)
    
    assert release_json["withheldInformation"][0]["rationale"] == rationale

def test_bt_196_bt_105_unpublished_justification_description_procedure_integration(tmp_path, caplog):
    caplog.set_level(logging.INFO)
    
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
          xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
          xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1">
        <cbc:ContractFolderID>1234</cbc:ContractFolderID>
        <cac:TenderingProcess>
            <ext:UBLExtensions>
                <ext:UBLExtension>
                    <ext:ExtensionContent>
                        <efext:EformsExtension>
                            <efac:FieldsPrivacy>
                                <efbc:FieldIdentifierCode>pro-typ</efbc:FieldIdentifierCode>
                                <efbc:ReasonDescription>Information delayed publication because of sensitive procedure type</efbc:ReasonDescription>
                            </efac:FieldsPrivacy>
                        </efext:EformsExtension>
                    </ext:ExtensionContent>
                </ext:UBLExtension>
            </ext:UBLExtensions>
        </cac:TenderingProcess>
    </root>
    """
    xml_file = tmp_path / "test_input_unpublished_justification_description_procedure_bt105.xml"
    xml_file.write_text(xml_content)

    # Mocking the existing withheldInformation item for BT-195(BT-105)-Procedure
    initial_json = {
        "withheldInformation": [
            {
                "id": "pro-typ-1234",
                "field": "pro-typ",
                "name": "Procedure Type"
            }
        ]
    }

    with open('output.json', 'w') as f:
        json.dump(initial_json, f)

    main(str(xml_file), "ocds-test-prefix")

    with open('output.json', 'r') as f:
        result = json.load(f)

    logger.info(f"Result: {json.dumps(result, indent=2)}")

    assert "withheldInformation" in result, "Expected 'withheldInformation' in result"
    assert len(result["withheldInformation"]) == 1, "Expected one withheld information item"

    withheld_item = result["withheldInformation"][0]
    assert withheld_item["id"] == "pro-typ-1234", "Expected 'id' to be 'pro-typ-1234'"
    assert withheld_item["field"] == "pro-typ", "Expected 'field' to be 'pro-typ'"
    assert withheld_item["name"] == "Procedure Type", "Expected 'name' to be 'Procedure Type'"
    assert "rationale" in withheld_item, "Expected 'rationale' in withheld information item"
    assert withheld_item["rationale"] == "Information delayed publication because of sensitive procedure type", "Unexpected rationale content"

    for record in caplog.records:
        print(f"{record.levelname}: {record.message}")

if __name__ == "__main__":
    pytest.main()