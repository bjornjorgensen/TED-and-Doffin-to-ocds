# tests/test_BT_197_BT_160_Tender.py

import pytest
import json
import os
import sys
from lxml import etree

# Add the parent directory to sys.path to import main and the converter functions
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main
from converters.BT_197_BT_160_Tender import parse_bt_197_bt_160_tender, merge_bt_197_bt_160_tender

def test_bt_197_bt_160_tender_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
          xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
          xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1">
        <ext:UBLExtensions>
            <ext:UBLExtension>
                <ext:ExtensionContent>
                    <efext:EformsExtension>
                        <efac:NoticeResult>
                            <efac:LotTender>
                                <efac:ConcessionRevenue>
                                    <efac:FieldsPrivacy>
                                        <efbc:FieldIdentifierCode>con-rev-buy</efbc:FieldIdentifierCode>
                                        <cbc:ReasonCode listName="non-publication-justification">oth-int</cbc:ReasonCode>
                                    </efac:FieldsPrivacy>
                                </efac:ConcessionRevenue>
                            </efac:LotTender>
                        </efac:NoticeResult>
                    </efext:EformsExtension>
                </ext:ExtensionContent>
            </ext:UBLExtension>
        </ext:UBLExtensions>
    </root>
    """

    xml_file = tmp_path / "test_input_bt_197_bt_160_tender.xml"
    xml_file.write_text(xml_content)

    result = main(str(xml_file), "ocds-test-prefix")
    print(f"Result from main: {json.dumps(result, indent=2)}")

    assert "withheldInformation" in result, "withheldInformation not found in result"
    assert len(result["withheldInformation"]) > 0, "No withheld information items found"

    bt_160_item = next((item for item in result["withheldInformation"] if item.get("field") == "BT-160"), None)
    assert bt_160_item is not None, "No withheld information item for BT-160 found"

    assert "rationaleClassifications" in bt_160_item, "rationaleClassifications not found in withheld information item"
    assert len(bt_160_item["rationaleClassifications"]) > 0, "No rationale classifications found"

    classification = bt_160_item["rationaleClassifications"][0]
    assert classification["scheme"] == "eu-non-publication-justification", f"Expected scheme 'eu-non-publication-justification', got {classification['scheme']}"
    assert classification["id"] == "oth-int", f"Expected id 'oth-int', got {classification['id']}"
    assert classification["description"] == "Other public interest", f"Expected description 'Other public interest', got {classification['description']}"
    assert classification["uri"] == "http://publications.europa.eu/resource/authority/non-publication-justification/oth-int", f"Expected URI 'http://publications.europa.eu/resource/authority/non-publication-justification/oth-int', got {classification['uri']}"

if __name__ == "__main__":
    pytest.main()
