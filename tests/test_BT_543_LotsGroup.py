# tests/test_BT_543_LotsGroup.py

import pytest
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main

def test_bt_543_lotsgroup_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="LotsGroup">GLO-0001</cbc:ID>
            <cac:TenderingTerms>
                <cac:AwardingTerms>
                    <cac:AwardingCriterion>
                        <cbc:CalculationExpression languageID="ENG">Price-quality score calculation is based on ...</cbc:CalculationExpression>
                    </cac:AwardingCriterion>
                </cac:AwardingTerms>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </root>
    """
    xml_file = tmp_path / "test_input_award_criteria_complicated_lotsgroup.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open('output.json', 'r') as f:
        result = json.load(f)

    assert "tender" in result, "Expected 'tender' in result"
    assert "lotGroups" in result["tender"], "Expected 'lotGroups' in tender"
    assert len(result["tender"]["lotGroups"]) == 1, f"Expected 1 lot group, got {len(result['tender']['lotGroups'])}"

    lot_group = result["tender"]["lotGroups"][0]
    assert lot_group["id"] == "GLO-0001", f"Expected lot group id 'GLO-0001', got {lot_group['id']}"
    assert "awardCriteria" in lot_group, "Expected 'awardCriteria' in lot group"
    assert "weightingDescription" in lot_group["awardCriteria"], "Expected 'weightingDescription' in lot group awardCriteria"
    expected_description = "Price-quality score calculation is based on ..."
    assert lot_group["awardCriteria"]["weightingDescription"] == expected_description, f"Expected weightingDescription '{expected_description}', got {lot_group['awardCriteria']['weightingDescription']}"

if __name__ == "__main__":
    pytest.main()