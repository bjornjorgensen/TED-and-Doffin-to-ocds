# tests/test_bt_06_Lot.py

import pytest
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.ted_and_doffin_to_ocds.main import main


def test_bt_06_lot_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:ProcurementProject>
                <cac:ProcurementAdditionalType>
                    <cbc:ProcurementTypeCode listName="strategic-procurement">inn-pur</cbc:ProcurementTypeCode>
                </cac:ProcurementAdditionalType>
            </cac:ProcurementProject>
        </cac:ProcurementProjectLot>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0002</cbc:ID>
            <cac:ProcurementProject>
                <cac:ProcurementAdditionalType>
                    <cbc:ProcurementTypeCode listName="strategic-procurement">env-imp</cbc:ProcurementTypeCode>
                </cac:ProcurementAdditionalType>
            </cac:ProcurementProject>
        </cac:ProcurementProjectLot>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0003</cbc:ID>
            <cac:ProcurementProject>
                <cac:ProcurementAdditionalType>
                    <cbc:ProcurementTypeCode listName="strategic-procurement">none</cbc:ProcurementTypeCode>
                </cac:ProcurementAdditionalType>
            </cac:ProcurementProject>
        </cac:ProcurementProjectLot>
    </root>
    """
    xml_file = tmp_path / "test_input_strategic_procurement.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open("output.json") as f:
        result = json.load(f)

    assert "tender" in result, "Expected 'tender' in result"
    assert "lots" in result["tender"], "Expected 'lots' in result['tender']"
    assert (
        len(result["tender"]["lots"]) == 3
    ), f"Expected 3 lots, got {len(result['tender']['lots'])}"

    lot_1 = next(lot for lot in result["tender"]["lots"] if lot["id"] == "LOT-0001")
    assert (
        lot_1["hasSustainability"] is True
    ), "Expected LOT-0001 to have sustainability"
    assert (
        len(lot_1["sustainability"]) == 1
    ), f"Expected 1 sustainability entry for LOT-0001, got {len(lot_1['sustainability'])}"
    assert (
        lot_1["sustainability"][0]["goal"] == "economic.innovativePurchase"
    ), f"Expected goal 'economic.innovativePurchase' for LOT-0001, got {lot_1['sustainability'][0]['goal']}"

    lot_2 = next(lot for lot in result["tender"]["lots"] if lot["id"] == "LOT-0002")
    assert (
        lot_2["hasSustainability"] is True
    ), "Expected LOT-0002 to have sustainability"
    assert (
        len(lot_2["sustainability"]) == 1
    ), f"Expected 1 sustainability entry for LOT-0002, got {len(lot_2['sustainability'])}"
    assert (
        lot_2["sustainability"][0]["goal"] == "environmental"
    ), f"Expected goal 'environmental' for LOT-0002, got {lot_2['sustainability'][0]['goal']}"

    lot_3 = next(lot for lot in result["tender"]["lots"] if lot["id"] == "LOT-0003")
    assert (
        "hasSustainability" not in lot_3
    ), "Expected LOT-0003 to not have sustainability information"
    assert (
        "sustainability" not in lot_3
    ), "Expected LOT-0003 to not have sustainability information"


if __name__ == "__main__":
    pytest.main()
