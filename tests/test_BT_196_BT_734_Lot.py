# tests/test_BT_196_BT_734_Lot.py

import pytest
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main

def test_bt_196_bt_734_lot_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
          xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1"
          xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">1</cbc:ID>
            <cac:TenderingTerms>
                <cac:AwardingTerms>
                    <cac:AwardingCriterion>
                        <cac:SubordinateAwardingCriterion>
                            <ext:UBLExtensions>
                                <ext:UBLExtension>
                                    <ext:ExtensionContent>
                                        <efext:EformsExtension>
                                            <efac:FieldsPrivacy>
                                                <efbc:FieldIdentifierCode>awa-cri-nam</efbc:FieldIdentifierCode>
                                                <efbc:ReasonDescription>Information delayed publication due to confidentiality concerns</efbc:ReasonDescription>
                                            </efac:FieldsPrivacy>
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
    xml_file = tmp_path / "test_input_bt_196_bt_734_lot.xml"
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
    expected_rationale = "Information delayed publication due to confidentiality concerns"
    assert withheld_info["rationale"] == expected_rationale, f"Expected rationale '{expected_rationale}', got {withheld_info['rationale']}"
    assert withheld_info["id"] == "awa-cri-nam-1", f"Expected id 'awa-cri-nam-1', got {withheld_info['id']}"
    assert withheld_info["field"] == "awa-cri-nam", f"Expected field 'awa-cri-nam', got {withheld_info['field']}"
    assert withheld_info["name"] == "Award Criteria Name Justification", f"Expected name 'Award Criteria Name Justification', got {withheld_info['name']}"

if __name__ == "__main__":
    pytest.main()