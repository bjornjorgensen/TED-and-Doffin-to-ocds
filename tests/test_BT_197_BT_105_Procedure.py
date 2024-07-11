# tests/test_BT_197_BT_105_Procedure.py

import pytest
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main

def test_bt_197_bt_105_procedure_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
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
                                <cbc:ReasonCode listName="non-publication-justification">oth-int</cbc:ReasonCode>
                            </efac:FieldsPrivacy>
                        </efext:EformsExtension>
                    </ext:ExtensionContent>
                </ext:UBLExtension>
            </ext:UBLExtensions>
        </cac:TenderingProcess>
    </root>
    """
    xml_file = tmp_path / "test_input_bt_197_bt_105_procedure.xml"
    xml_file.write_text(xml_content)

    result = main(str(xml_file), "ocds-test-prefix")

    assert "withheldInformation" in result, "withheldInformation not found in result"
    assert len(result["withheldInformation"]) > 0, "No withheld information items found"
    
    pro_typ_item = next((item for item in result["withheldInformation"] if item.get("id", "").startswith("pro-typ-")), None)
    assert pro_typ_item is not None, "No withheld information item for procedure type found"
    assert "rationaleClassifications" in pro_typ_item, "rationaleClassifications not found in withheld information item"
    assert len(pro_typ_item["rationaleClassifications"]) > 0, "No rationale classifications found"
    
    classification = pro_typ_item["rationaleClassifications"][0]
    assert classification["scheme"] == "non-publication-justification", "Incorrect scheme"
    assert classification["id"] == "oth-int", "Incorrect id"
    assert classification["description"] == "Other public interest", "Incorrect description"
    assert classification["uri"] == "http://publications.europa.eu/resource/authority/non-publication-justification/oth-int", "Incorrect URI"

if __name__ == "__main__":
    pytest.main()