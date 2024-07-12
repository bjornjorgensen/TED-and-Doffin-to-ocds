# tests/test_BT_197_BT_135_Procedure.py

import pytest
import json
import os
import sys

# Add the parent directory to sys.path to import the converter functions
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from converters.BT_197_BT_135_Procedure import parse_unpublished_justification_code_procedure_bt135, merge_unpublished_justification_code_procedure_bt135

def test_bt_197_bt_135_procedure_integration():
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
          xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
          xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1">
        <cac:TenderingProcess>
            <cac:ProcessJustification>
                <cbc:ProcessReasonCode listName="direct-award-justification">code</cbc:ProcessReasonCode>
                <ext:UBLExtensions>
                    <ext:UBLExtension>
                        <ext:ExtensionContent>
                            <efext:EformsExtension>
                                <efac:FieldsPrivacy>
                                    <efbc:FieldIdentifierCode>dir-awa-tex</efbc:FieldIdentifierCode>
                                    <cbc:ReasonCode>oth-int</cbc:ReasonCode>
                                </efac:FieldsPrivacy>
                            </efext:EformsExtension>
                        </ext:ExtensionContent>
                    </ext:UBLExtension>
                </ext:UBLExtensions>
            </cac:ProcessJustification>
        </cac:TenderingProcess>
    </root>
    """

    # Parse the justification code
    justification_code = parse_unpublished_justification_code_procedure_bt135(xml_content)

    assert justification_code is not None, "Expected justification code to be parsed"
    assert justification_code["scheme"] == "eu-non-publication-justification", f"Expected scheme 'eu-non-publication-justification', got {justification_code['scheme']}"
    assert justification_code["id"] == "oth-int", f"Expected id 'oth-int', got {justification_code['id']}"
    assert justification_code["description"] == "Other public interest", f"Expected description 'Other public interest', got {justification_code['description']}"
    assert justification_code["uri"] == "http://publications.europa.eu/resource/authority/non-publication-justification/oth-int", f"Expected URI 'http://publications.europa.eu/resource/authority/non-publication-justification/oth-int', got {justification_code['uri']}"

    # Test merging the justification code
    release_json = {
        "withheldInformation": [
            {
                "id": "dir-awa-tex-1",
                "field": "dir-awa-tex",
                "name": "Direct Award Justification Text"
            }
        ]
    }

    merge_unpublished_justification_code_procedure_bt135(release_json, justification_code)

    assert "withheldInformation" in release_json, "Expected 'withheldInformation' in result"
    assert len(release_json["withheldInformation"]) == 1, f"Expected 1 withheld information item, got {len(release_json['withheldInformation'])}"

    withheld_info = release_json["withheldInformation"][0]
    assert "rationaleClassifications" in withheld_info, "Expected 'rationaleClassifications' in withheld information"
    assert len(withheld_info["rationaleClassifications"]) == 1, f"Expected 1 rationale classification, got {len(withheld_info['rationaleClassifications'])}"

    classification = withheld_info["rationaleClassifications"][0]
    assert classification["scheme"] == "eu-non-publication-justification", f"Expected scheme 'eu-non-publication-justification', got {classification['scheme']}"
    assert classification["id"] == "oth-int", f"Expected id 'oth-int', got {classification['id']}"
    assert classification["description"] == "Other public interest", f"Expected description 'Other public interest', got {classification['description']}"
    assert classification["uri"] == "http://publications.europa.eu/resource/authority/non-publication-justification/oth-int", f"Expected URI 'http://publications.europa.eu/resource/authority/non-publication-justification/oth-int', got {classification['uri']}"

if __name__ == "__main__":
    pytest.main()