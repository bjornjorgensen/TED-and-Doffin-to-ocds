# tests/test_BT_198_BT_105_Procedure.py

import pytest
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main

def test_bt_198_bt_105_procedure_integration(tmp_path):
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
                                <efbc:PublicationDate>2025-03-31+01:00</efbc:PublicationDate>
                            </efac:FieldsPrivacy>
                        </efext:EformsExtension>
                    </ext:ExtensionContent>
                </ext:UBLExtension>
            </ext:UBLExtensions>
        </cac:TenderingProcess>
    </root>
    """
    xml_file = tmp_path / "test_input_bt_198_bt_105_procedure.xml"
    xml_file.write_text(xml_content)

    result = main(str(xml_file), "ocds-test-prefix")

    assert "withheldInformation" in result, "withheldInformation not found in result"
    assert len(result["withheldInformation"]) > 0, "No withheld information items found"
    
    pro_typ_item = next((item for item in result["withheldInformation"] if item.get("id", "").startswith("pro-typ-")), None)
    assert pro_typ_item is not None, "No withheld information item for procedure type found"
    assert "availabilityDate" in pro_typ_item, "availabilityDate not found in withheld information item"
    assert pro_typ_item["availabilityDate"] == "2025-03-31T00:00:00+01:00", f"Expected availabilityDate '2025-03-31T00:00:00+01:00', got {pro_typ_item['availabilityDate']}"

if __name__ == "__main__":
    pytest.main()