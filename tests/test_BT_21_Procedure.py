# tests/test_BT_21_Procedure.py

import pytest
import json
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.ted_and_doffin_to_ocds.main import main


def test_bt_21_procedure_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProject>
            <cbc:Name languageID="ENG">Computer Network extension</cbc:Name>
        </cac:ProcurementProject>
    </root>
    """

    xml_file = tmp_path / "test_input_procedure_title.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open("output.json") as f:
        result = json.load(f)

    assert "tender" in result
    assert "title" in result["tender"]
    assert result["tender"]["title"] == "Computer Network extension"


if __name__ == "__main__":
    pytest.main()
