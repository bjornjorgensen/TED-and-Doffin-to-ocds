# tests/test_BT_762_ChangeReasonDescription.py

import pytest
import json
import os
import sys
import logging

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main, configure_logging

def test_bt_762_change_reason_description_integration(tmp_path):
    configure_logging()
    logger = logging.getLogger(__name__)

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
                        <efac:Changes>
                            <efac:ChangeReason>
                                <efbc:ReasonDescription languageID="ENG">Clerical corrections of ...</efbc:ReasonDescription>
                            </efac:ChangeReason>
                            <efac:ChangeReason>
                                <efbc:ReasonDescription languageID="ENG">Additional information added</efbc:ReasonDescription>
                            </efac:ChangeReason>
                        </efac:Changes>
                    </efext:EformsExtension>
                </ext:ExtensionContent>
            </ext:UBLExtension>
        </ext:UBLExtensions>
    </root>
    """
    xml_file = tmp_path / "test_input_change_reason_description.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open('output.json', 'r') as f:
        result = json.load(f)

    logger.info(f"Result: {json.dumps(result, indent=2)}")

    assert "tender" in result, "Expected 'tender' in result"
    assert "amendments" in result["tender"], "Expected 'amendments' in tender"
    assert len(result["tender"]["amendments"]) == 2, f"Expected 2 amendments, got {len(result['tender']['amendments'])}"

    amendment1 = result["tender"]["amendments"][0]
    amendment2 = result["tender"]["amendments"][1]

    assert "rationale" in amendment1, "Expected 'rationale' in first amendment"
    assert "rationale" in amendment2, "Expected 'rationale' in second amendment"
    assert amendment1["rationale"] == "Clerical corrections of ...", f"Expected 'Clerical corrections of ...' for first amendment, got {amendment1['rationale']}"
    assert amendment2["rationale"] == "Additional information added", f"Expected 'Additional information added' for second amendment, got {amendment2['rationale']}"

if __name__ == "__main__":
    pytest.main(['-v', '-s'])