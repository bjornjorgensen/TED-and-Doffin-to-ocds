# tests/test_BT_196_BT_5422_LotsGroup.py

import pytest
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main

def test_bt_196_bt_5422_lotsgroup_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
          xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
          xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="LotsGroup">group-1</cbc:ID>
            <cac:TenderingTerms>
                <cac:AwardingTerms>
                    <cac:AwardingCriterion>
                        <cac:SubordinateAwardingCriterion>
                            <ext:UBLExtensions>
                                <ext:UBLExtension>
                                    <ext:ExtensionContent>
                                        <efext:EformsExtension>
                                            <efac:AwardCriterionParameter>
                                                <efbc:ParameterCode listName="number-fixed">fixed</efbc:ParameterCode>
                                                <efac:FieldsPrivacy>
                                                    <efbc:FieldIdentifierCode>awa-cri-fix</efbc:FieldIdentifierCode>
                                                    <efbc:ReasonDescription languageID="ENG">Information delayed publication because of ...</efbc:ReasonDescription>
                                                </efac:FieldsPrivacy>
                                            </efac:AwardCriterionParameter>
                                        </efext:EformsExtension>
                                    </ext:ExtensionContent>
                                </ext:UBLExtension>
                            </ext:UBLExtensions>
                        </cac:SubordinateAwardingCriterion>
                    </cac:AwardingCriterion>
                </cac:AwardingTerms>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </root>
    """
    xml_file = tmp_path / "test_input_bt_196_bt_5422_lotsgroup.xml"
    xml_file.write_text(xml_content)

    result = main(str(xml_file), "ocds-test-prefix")

    print(f"Result: {json.dumps(result, indent=2)}")  # Debug print

    assert "withheldInformation" in result, "withheldInformation not found in result"
    assert len(result["withheldInformation"]) > 0, "No withheld information items found"
    
    awa_cri_fix_item = next((item for item in result["withheldInformation"] if item.get("id") == "awa-cri-fix-group-group-1"), None)
    assert awa_cri_fix_item is not None, "No withheld information item for awarding criterion fixed number (LotsGroup) found"
    assert "rationale" in awa_cri_fix_item, "rationale not found in withheld information item"
    assert awa_cri_fix_item["rationale"] == "Information delayed publication because of ...", f"Expected rationale 'Information delayed publication because of ...', got {awa_cri_fix_item['rationale']}"

if __name__ == "__main__":
    pytest.main()