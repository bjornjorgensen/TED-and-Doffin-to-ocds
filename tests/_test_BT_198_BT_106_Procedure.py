# tests/test_BT_198_BT_106_Procedure.py

import pytest
import json
import os
import sys
from lxml import etree

# Add the parent directory to sys.path to import main and the converter functions
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main
from converters.BT_198_BT_106_Procedure import parse_bt_198_bt_106_procedure, merge_bt_198_bt_106_procedure

def test_parse_bt_198_bt_106_procedure():
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
          xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
          xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1">
        <cac:TenderingProcess>
            <cac:ProcessJustification>
                <cbc:ProcessReasonCode listName="accelerated-procedure">code</cbc:ProcessReasonCode>
                <ext:UBLExtensions>
                    <ext:UBLExtension>
                        <ext:ExtensionContent>
                            <efext:EformsExtension>
                                <efac:FieldsPrivacy>
                                    <efbc:FieldIdentifierCode>pro-acc</efbc:FieldIdentifierCode>
                                    <efbc:PublicationDate>2025-03-31+01:00</efbc:PublicationDate>
                                </efac:FieldsPrivacy>
                            </efext:EformsExtension>
                        </ext:ExtensionContent>
                    </ext:UBLExtension>
                </ext:UBLExtensions>
            </cac:ProcessJustification>
        </cac:TenderingProcess>
    </root>
    """
    result = parse_bt_198_bt_106_procedure(xml_content)
    assert result == "2025-03-31T00:00:00+01:00"

def test_merge_bt_198_bt_106_procedure():
    release_json = {
        "withheldInformation": []
    }
    bt_198_bt_106_procedure_data = "2025-03-31T00:00:00+01:00"
    
    merge_bt_198_bt_106_procedure(release_json, bt_198_bt_106_procedure_data)
    
    assert len(release_json["withheldInformation"]) == 1
    assert "availabilityDate" in release_json["withheldInformation"][0]
    assert release_json["withheldInformation"][0]["availabilityDate"] == "2025-03-31T00:00:00+01:00"
    assert "id" not in release_json["withheldInformation"][0]

def test_merge_bt_198_bt_106_procedure_existing_item():
    release_json = {
        "withheldInformation": [
            {"availabilityDate": "2024-01-01T00:00:00Z"}
        ]
    }
    bt_198_bt_106_procedure_data = "2025-03-31T00:00:00+01:00"
    
    merge_bt_198_bt_106_procedure(release_json, bt_198_bt_106_procedure_data)
    
    assert len(release_json["withheldInformation"]) == 1
    assert release_json["withheldInformation"][0]["availabilityDate"] == "2025-03-31T00:00:00+01:00"
    assert "id" not in release_json["withheldInformation"][0]

def test_bt_198_bt_106_procedure_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
          xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
          xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1">
        <cac:TenderingProcess>
            <cac:ProcessJustification>
                <cbc:ProcessReasonCode listName="accelerated-procedure">code</cbc:ProcessReasonCode>
                <ext:UBLExtensions>
                    <ext:UBLExtension>
                        <ext:ExtensionContent>
                            <efext:EformsExtension>
                                <efac:FieldsPrivacy>
                                    <efbc:FieldIdentifierCode>pro-acc</efbc:FieldIdentifierCode>
                                    <efbc:PublicationDate>2025-03-31+01:00</efbc:PublicationDate>
                                </efac:FieldsPrivacy>
                            </efext:EformsExtension>
                        </ext:ExtensionContent>
                    </ext:UBLExtension>
                </ext:UBLExtensions>
            </cac:ProcessJustification>
        </cac:TenderingProcess>
    </root>
    """
    xml_file = tmp_path / "test_input_bt_198_bt_106_procedure.xml"
    xml_file.write_text(xml_content)

    result = main(str(xml_file), "ocds-test-prefix")
    print(f"Result from main: {json.dumps(result, indent=2)}")

    assert "withheldInformation" in result, "withheldInformation not found in result"
    assert len(result["withheldInformation"]) > 0, "No withheld information items found"

    bt_106_procedure_item = next((item for item in result["withheldInformation"] if "availabilityDate" in item), None)
    assert bt_106_procedure_item is not None, "No withheld information item for BT-198(BT-106)-Procedure found"

    assert "id" not in bt_106_procedure_item, "Unexpected 'id' field found in withheld information item"
    assert "availabilityDate" in bt_106_procedure_item, "availabilityDate not found in withheld information item"
    assert bt_106_procedure_item["availabilityDate"] == "2025-03-31T00:00:00+01:00", f"Expected availabilityDate '2025-03-31T00:00:00+01:00', got {bt_106_procedure_item['availabilityDate']}"

if __name__ == "__main__":
    pytest.main()