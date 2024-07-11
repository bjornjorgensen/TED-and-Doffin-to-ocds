# tests/test_BT_197_BT_09_Procedure.py

import pytest
import json
import os
import sys
import logging

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main
from converters.BT_197_BT_09_Procedure import parse_unpublished_justification_code_procedure_bt09, merge_unpublished_justification_code_procedure_bt09

logger = logging.getLogger(__name__)

def test_parse_unpublished_justification_code_procedure_bt09():
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
          xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
          xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1">
        <cac:TenderingTerms>
            <cac:ProcurementLegislationDocumentReference>
                <cbc:ID>CrossBorderLaw</cbc:ID>
                <ext:UBLExtensions>
                    <ext:UBLExtension>
                        <ext:ExtensionContent>
                            <efext:EformsExtension>
                                <efac:FieldsPrivacy>
                                    <efbc:FieldIdentifierCode>cro-bor-law</efbc:FieldIdentifierCode>
                                    <cbc:ReasonCode>oth-int</cbc:ReasonCode>
                                </efac:FieldsPrivacy>
                            </efext:EformsExtension>
                        </ext:ExtensionContent>
                    </ext:UBLExtension>
                </ext:UBLExtensions>
            </cac:ProcurementLegislationDocumentReference>
        </cac:TenderingTerms>
    </root>
    """
    
    result = parse_unpublished_justification_code_procedure_bt09(xml_content)
    assert result == {
        'scheme': 'non-publication-justification',
        'id': 'oth-int',
        'description': 'Other public interest',
        'uri': 'http://publications.europa.eu/resource/authority/non-publication-justification/oth-int'
    }

def test_merge_unpublished_justification_code_procedure_bt09():
    release_json = {
        "withheldInformation": [
            {
                "id": "cro-bor-law-1234",
                "field": "cro-bor-law",
                "name": "Cross Border Law"
            }
        ]
    }
    
    justification_code = {
        'scheme': 'non-publication-justification',
        'id': 'oth-int',
        'description': 'Other public interest',
        'uri': 'http://publications.europa.eu/resource/authority/non-publication-justification/oth-int'
    }
    
    merge_unpublished_justification_code_procedure_bt09(release_json, justification_code)
    
    assert release_json["withheldInformation"][0]["rationaleClassifications"] == [justification_code]

def test_bt_197_bt_09_unpublished_justification_code_procedure_integration(tmp_path, caplog):
    caplog.set_level(logging.INFO)
    
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
          xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
          xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1">
        <cbc:ContractFolderID>1234</cbc:ContractFolderID>
        <cac:TenderingTerms>
            <cac:ProcurementLegislationDocumentReference>
                <cbc:ID>CrossBorderLaw</cbc:ID>
                <ext:UBLExtensions>
                    <ext:UBLExtension>
                        <ext:ExtensionContent>
                            <efext:EformsExtension>
                                <efac:FieldsPrivacy>
                                    <efbc:FieldIdentifierCode>cro-bor-law</efbc:FieldIdentifierCode>
                                    <cbc:ReasonCode>oth-int</cbc:ReasonCode>
                                </efac:FieldsPrivacy>
                            </efext:EformsExtension>
                        </ext:ExtensionContent>
                    </ext:UBLExtension>
                </ext:UBLExtensions>
            </cac:ProcurementLegislationDocumentReference>
        </cac:TenderingTerms>
    </root>
    """
    xml_file = tmp_path / "test_input_unpublished_justification_code_procedure_bt09.xml"
    xml_file.write_text(xml_content)

    # Mocking the existing withheldInformation item for BT-195(BT-09)-Procedure
    initial_json = {
        "withheldInformation": [
            {
                "id": "cro-bor-law-1234",
                "field": "cro-bor-law",
                "name": "Cross Border Law"
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
    assert withheld_item["id"] == "cro-bor-law-1234", "Expected 'id' to be 'cro-bor-law-1234'"
    assert withheld_item["field"] == "cro-bor-law", "Expected 'field' to be 'cro-bor-law'"
    assert withheld_item["name"] == "Cross Border Law", "Expected 'name' to be 'Cross Border Law'"
    assert "rationaleClassifications" in withheld_item, "Expected 'rationaleClassifications' in withheld information item"
    assert len(withheld_item["rationaleClassifications"]) == 1, "Expected one rationale classification"
    
    classification = withheld_item["rationaleClassifications"][0]
    assert classification["scheme"] == "non-publication-justification"
    assert classification["id"] == "oth-int"
    assert classification["description"] == "Other public interest"
    assert classification["uri"] == "http://publications.europa.eu/resource/authority/non-publication-justification/oth-int"

    for record in caplog.records:
        print(f"{record.levelname}: {record.message}")

if __name__ == "__main__":
    pytest.main()