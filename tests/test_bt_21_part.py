# tests/test_bt_21_part.py
from pathlib import Path
import pytest
import json
import sys

sys.path.append(str(Path(__file__).parent.parent))
from src.ted_and_doffin_to_ocds.main import main


def test_bt_21_part_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="part">PART-0001</cbc:ID>
            <cac:ProcurementProject>
                <cbc:Name languageID="ENG">Computer Network extension</cbc:Name>
            </cac:ProcurementProject>
        </cac:ProcurementProjectLot>
    </root>
    """

    xml_file = tmp_path / "test_input_part_title.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with Path("output.json").open() as f:
        result = json.load(f)

    assert "tender" in result
    assert "title" in result["tender"]
    assert result["tender"]["title"] == "Computer Network extension"


if __name__ == "__main__":
    pytest.main()