# tests/test_BT_197_BT_543_LotsGroup.py

import pytest
import json
import os
import sys
from lxml import etree

# Add the parent directory to sys.path to import main and the converter functions
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main

def test_bt_197_bt_543_lotsgroup_integration(tmp_path):
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
                        <ext:UBLExtensions>
                            <ext:UBLExtension>
                                <ext:ExtensionContent>
                                    <efext:EformsExtension>
                                        <efac:FieldsPrivacy>
                                            <efbc:FieldIdentifierCode>awa-cri-com</efbc:FieldIdentifierCode>
                                            <cbc:ReasonCode listName="non-publication-justification">oth-int</cbc:ReasonCode>
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
    xml_file = tmp_path / "test_input_bt_197_bt_543_lotsgroup.xml"
    xml_file.write_text(xml_content)

    result = main(str(xml_file), "ocds-test-prefix")
    print(f"Result from main: {json.dumps(result, indent=2)}")

    assert "withheldInformation" in result, "withheldInformation not found in result"
    assert len(result["withheldInformation"]) > 0, "No withheld information items found"

    bt_543_item = next((item for item in result["withheldInformation"] if item.get("id") == "BT-195(BT-543)-LotsGroup"), None)
    assert bt_543_item is not None, "No withheld information item for BT-195(BT-543)-LotsGroup found"

    assert "rationaleClassifications" in bt_543_item, "rationaleClassifications not found in withheld information item"
    assert len(bt_543_item["rationaleClassifications"]) > 0, "No rationale classifications found"

    classification = bt_543_item["rationaleClassifications"][0]
    assert classification["scheme"] == "eu-non-publication-justification", f"Expected scheme 'eu-non-publication-justification', got {classification['scheme']}"
    assert classification["id"] == "oth-int", f"Expected id 'oth-int', got {classification['id']}"
    assert classification["description"] == "Other public interest", f"Expected description 'Other public interest', got {classification['description']}"
    assert classification["uri"] == "http://publications.europa.eu/resource/authority/non-publication-justification/oth-int", f"Expected URI 'http://publications.europa.eu/resource/authority/non-publication-justification/oth-int', got {classification['uri']}"

if __name__ == "__main__":
    pytest.main()