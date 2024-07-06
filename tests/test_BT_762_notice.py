# tests/test_BT_762_notice.py

import pytest
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main

def test_bt_762_notice_integration(tmp_path):
    xml_content = """
    <root xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
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

    assert "tender" in result, "Expected 'tender' in result"
    assert "amendments" in result["tender"], "Expected 'amendments' in result['tender']"
    assert len(result["tender"]["amendments"]) == 1, f"Expected 1 amendment, got {len(result['tender']['amendments'])}"

    amendment = result["tender"]["amendments"][0]
    assert "rationale" in amendment, "Expected 'rationale' in amendment"
    assert amendment["rationale"] == "Clerical corrections of ...", f"Unexpected rationale content"

if __name__ == "__main__":
    pytest.main()