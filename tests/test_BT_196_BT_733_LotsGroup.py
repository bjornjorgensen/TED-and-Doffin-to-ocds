# tests/test_BT_196_BT_733_LotsGroup.py

import pytest
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main

def test_bt_196_bt_733_lots_group_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
          xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1"
          xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="LotsGroup">Group1</cbc:ID>
            <cac:TenderingTerms>
                <cac:AwardingTerms>
                    <cac:AwardingCriterion>
                        <ext:UBLExtensions>
                            <ext:UBLExtension>
                                <ext:ExtensionContent>
                                    <efext:EformsExtension>
                                        <efac:FieldsPrivacy>
                                            <efbc:FieldIdentifierCode>awa-cri-ord</efbc:FieldIdentifierCode>
                                            <efbc:ReasonDescription>Information delayed publication due to complex evaluation criteria</efbc:ReasonDescription>
                                        </efac:FieldsPrivacy>
                                    </efext:EformsExtension>
                                </ext:ExtensionContent>
                            </ext:UBLExtension>
                        </ext:UBLExtensions>
                    </cac:AwardingCriterion>
                </cac:AwardingTerms>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </root>
    """
    xml_file = tmp_path / "test_input_bt_196_bt_733_lots_group.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open('output.json', 'r') as f:
        result = json.load(f)

    assert "withheldInformation" in result, "Expected 'withheldInformation' in result"
    assert len(result["withheldInformation"]) == 1, f"Expected 1 withheld information item, got {len(result['withheldInformation'])}"

    withheld_info = result["withheldInformation"][0]
    assert "rationale" in withheld_info, "Expected 'rationale' in withheld information"
    assert "id" in withheld_info, "Expected 'id' in withheld information"
    assert "field" in withheld_info, "Expected 'field' in withheld information"
    assert "name" in withheld_info, "Expected 'name' in withheld information"
    expected_rationale = "Information delayed publication due to complex evaluation criteria"
    assert withheld_info["rationale"] == expected_rationale, f"Expected rationale '{expected_rationale}', got {withheld_info['rationale']}"
    assert withheld_info["id"] == "awa-cri-ord-Group1", f"Expected id 'awa-cri-ord-Group1', got {withheld_info['id']}"
    assert withheld_info["field"] == "awa-cri-ord", f"Expected field 'awa-cri-ord', got {withheld_info['field']}"
    assert withheld_info["name"] == "Award Criteria Order Justification", f"Expected name 'Award Criteria Order Justification', got {withheld_info['name']}"

if __name__ == "__main__":
    pytest.main()