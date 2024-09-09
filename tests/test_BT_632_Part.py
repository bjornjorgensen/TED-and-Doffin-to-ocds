# tests/test_BT_632_Part.py

import pytest
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main


def test_bt_632_part_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
          xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
          xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Part">PART-0001</cbc:ID>
            <cac:TenderingProcess>
                <ext:UBLExtensions>
                    <ext:UBLExtension>
                        <ext:ExtensionContent>
                            <efext:EformsExtension>
                                <efbc:AccessToolName>AbcKomSoft</efbc:AccessToolName>
                            </efext:EformsExtension>
                        </ext:ExtensionContent>
                    </ext:UBLExtension>
                </ext:UBLExtensions>
            </cac:TenderingProcess>
        </cac:ProcurementProjectLot>
    </root>
    """
    xml_file = tmp_path / "test_input_bt_632_part.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open("output.json") as f:
        result = json.load(f)

    assert "tender" in result, "Expected 'tender' in result"
    assert "communication" in result["tender"], "Expected 'communication' in tender"
    assert (
        "atypicalToolName" in result["tender"]["communication"]
    ), "Expected 'atypicalToolName' in tender communication"
    expected_tool_name = "AbcKomSoft"
    assert (
        result["tender"]["communication"]["atypicalToolName"] == expected_tool_name
    ), f"Expected tool name '{expected_tool_name}', got {result['tender']['communication']['atypicalToolName']}"


if __name__ == "__main__":
    pytest.main()
