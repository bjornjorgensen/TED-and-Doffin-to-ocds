# tests/test_BT_195_BT_5422_LotsGroup.py

import pytest
import json
import os
import sys
import logging

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main

logger = logging.getLogger(__name__)

def test_bt_195_bt_5422_unpublished_award_criterion_number_fixed_lotsgroup_integration(tmp_path, caplog):
    caplog.set_level(logging.INFO)
    
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
          xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
          xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="LotsGroup">GLO-0001</cbc:ID>
            <cac:TenderingTerms>
                <cac:AwardingTerms>
                    <cac:AwardingCriterion>
                        <cac:SubordinateAwardingCriterion>
                            <ext:UBLExtensions>
                                <ext:UBLExtension>
                                    <ext:ExtensionContent>
                                        <efext:EformsExtension>
                                            <efac:AwardCriterionParameter>
                                                <efbc:ParameterCode listName="number-fixed"/>
                                                <efac:FieldsPrivacy>
                                                    <efbc:FieldIdentifierCode listName="non-publication-identifier">awa-cri-fix</efbc:FieldIdentifierCode>
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
    xml_file = tmp_path / "test_input_unpublished_award_criterion_number_fixed_lotsgroup.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open('output.json', 'r') as f:
        result = json.load(f)

    logger.info(f"Result: {json.dumps(result, indent=2)}")

    assert "withheldInformation" in result, "Expected 'withheldInformation' in result"
    assert len(result.get("withheldInformation", [])) > 0, "Expected at least one withheld information item"

    expected_item = {
        "id": "awa-cri-fix-GLO-0001",
        "field": "awa-cri-fix",
        "name": "Award Criterion Number Fixed"
    }
    assert expected_item in result.get("withheldInformation", []), f"Expected {expected_item} in withheldInformation"

    for record in caplog.records:
        print(f"{record.levelname}: {record.message}")

if __name__ == "__main__":
    pytest.main()