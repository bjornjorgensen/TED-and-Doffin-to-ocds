# tests/test_bt_21_LotsGroup.py

import pytest
import json
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.ted_and_doffin_to_ocds.main import main


def test_bt_21_lots_group_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="LotsGroup">GLO-0001</cbc:ID>
            <cac:ProcurementProject>
                <cbc:Name>Computer Network extension</cbc:Name>
            </cac:ProcurementProject>
        </cac:ProcurementProjectLot>
    </root>
    """

    xml_file = tmp_path / "test_input_lots_group_title.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open("output.json") as f:
        result = json.load(f)

    assert "tender" in result
    assert "lotGroups" in result["tender"]
    assert len(result["tender"]["lotGroups"]) == 1
    assert result["tender"]["lotGroups"][0]["id"] == "GLO-0001"
    assert result["tender"]["lotGroups"][0]["title"] == "Computer Network extension"


if __name__ == "__main__":
    pytest.main()
