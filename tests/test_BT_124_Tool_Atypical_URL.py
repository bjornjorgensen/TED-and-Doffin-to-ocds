# tests/test_BT_124_Tool_Atypical_URL.py

import pytest
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main


def test_bt_124_tool_atypical_url_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:TenderingProcess>
                <cbc:AccessToolsURI>https://my-atypical-tool-lot.com/</cbc:AccessToolsURI>
            </cac:TenderingProcess>
        </cac:ProcurementProjectLot>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Part">PART-0001</cbc:ID>
            <cac:TenderingProcess>
                <cbc:AccessToolsURI>https://my-atypical-tool-part.com/</cbc:AccessToolsURI>
            </cac:TenderingProcess>
        </cac:ProcurementProjectLot>
    </root>
    """
    xml_file = tmp_path / "test_input_tool_atypical_url.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open("output.json", "r") as f:
        result = json.load(f)

    assert "tender" in result
    assert "lots" in result["tender"]
    assert len(result["tender"]["lots"]) == 1
    lot = result["tender"]["lots"][0]
    assert lot["id"] == "LOT-0001"
    assert "communication" in lot
    assert "atypicalToolUrl" in lot["communication"]
    assert (
        lot["communication"]["atypicalToolUrl"] == "https://my-atypical-tool-lot.com/"
    )

    assert "communication" in result["tender"]
    assert "atypicalToolUrl" in result["tender"]["communication"]
    assert (
        result["tender"]["communication"]["atypicalToolUrl"]
        == "https://my-atypical-tool-part.com/"
    )


if __name__ == "__main__":
    pytest.main()
