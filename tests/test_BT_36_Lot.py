# tests/test_BT_36_Lot.py

import pytest
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main


def test_bt_36_lot_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:ProcurementProject>
                <cac:PlannedPeriod>
                    <cbc:DurationMeasure unitCode="DAY">3</cbc:DurationMeasure>
                </cac:PlannedPeriod>
            </cac:ProcurementProject>
        </cac:ProcurementProjectLot>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0002</cbc:ID>
            <cac:ProcurementProject>
                <cac:PlannedPeriod>
                    <cbc:DurationMeasure unitCode="MONTH">2</cbc:DurationMeasure>
                </cac:PlannedPeriod>
            </cac:ProcurementProject>
        </cac:ProcurementProjectLot>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0003</cbc:ID>
            <cac:ProcurementProject>
                <cac:PlannedPeriod>
                    <cbc:DurationMeasure unitCode="YEAR">1</cbc:DurationMeasure>
                </cac:PlannedPeriod>
            </cac:ProcurementProject>
        </cac:ProcurementProjectLot>
    </root>
    """
    xml_file = tmp_path / "test_input_lot_duration.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open("output.json", "r") as f:
        result = json.load(f)

    assert "tender" in result, "Expected 'tender' in result"
    assert "lots" in result["tender"], "Expected 'lots' in tender"
    assert (
        len(result["tender"]["lots"]) == 3
    ), f"Expected 3 lots, got {len(result['tender']['lots'])}"

    lot1 = next(lot for lot in result["tender"]["lots"] if lot["id"] == "LOT-0001")
    assert (
        lot1["contractPeriod"]["durationInDays"] == 3
    ), f"Expected duration 3 days for LOT-0001, got {lot1['contractPeriod']['durationInDays']}"

    lot2 = next(lot for lot in result["tender"]["lots"] if lot["id"] == "LOT-0002")
    assert (
        lot2["contractPeriod"]["durationInDays"] == 60
    ), f"Expected duration 60 days for LOT-0002, got {lot2['contractPeriod']['durationInDays']}"

    lot3 = next(lot for lot in result["tender"]["lots"] if lot["id"] == "LOT-0003")
    assert (
        lot3["contractPeriod"]["durationInDays"] == 365
    ), f"Expected duration 365 days for LOT-0003, got {lot3['contractPeriod']['durationInDays']}"


if __name__ == "__main__":
    pytest.main()
