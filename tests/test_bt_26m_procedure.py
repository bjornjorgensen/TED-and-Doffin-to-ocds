# tests/test_bt_26m_procedure.py

import pytest
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.ted_and_doffin_to_ocds.main import main


def test_bt_26m_procedure_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProject>
            <cac:MainCommodityClassification>
                <cbc:ItemClassificationCode listName="cpv">15311100</cbc:ItemClassificationCode>
            </cac:MainCommodityClassification>
        </cac:ProcurementProject>
    </root>
    """
    xml_file = tmp_path / "test_input_main_classification_type_procedure.xml"
    xml_file.write_text(xml_content)

    result = main(str(xml_file), "ocds-test-prefix")

    assert "tender" in result
    assert "items" in result["tender"]
    assert len(result["tender"]["items"]) == 1
    item = result["tender"]["items"][0]
    assert item["id"] == "1"
    assert "classification" in item
    assert item["classification"]["scheme"] == "CPV"


if __name__ == "__main__":
    pytest.main()
