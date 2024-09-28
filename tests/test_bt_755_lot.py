# tests/test_bt_755_Lot.py
from pathlib import Path
import pytest
import json
import sys

# Add the parent directory to sys.path to import main
sys.path.append(str(Path(__file__).parent.parent))
from src.ted_and_doffin_to_ocds.main import main


def test_bt_755_lot_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:ProcurementProject>
                <cac:ProcurementAdditionalType>
                    <cbc:ProcurementTypeCode listName="accessibility">n-inc-just</cbc:ProcurementTypeCode>
                    <cbc:ProcurementType>Accessibility criteria are not included because of specific technical requirements.</cbc:ProcurementType>
                </cac:ProcurementAdditionalType>
            </cac:ProcurementProject>
        </cac:ProcurementProjectLot>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0002</cbc:ID>
            <cac:ProcurementProject>
                <cac:ProcurementAdditionalType>
                    <cbc:ProcurementTypeCode listName="accessibility">inc</cbc:ProcurementTypeCode>
                </cac:ProcurementAdditionalType>
            </cac:ProcurementProject>
        </cac:ProcurementProjectLot>
    </root>
    """
    xml_file = tmp_path / "test_input_accessibility_justification.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with Path("output.json").open() as f:
        result = json.load(f)

    assert "tender" in result, "Expected 'tender' in result"
    assert "lots" in result["tender"], "Expected 'lots' in tender"
    assert (
        len(result["tender"]["lots"]) == 2
    ), f"Expected 2 lots, got {len(result['tender']['lots'])}"

    lot1 = next(lot for lot in result["tender"]["lots"] if lot["id"] == "LOT-0001")
    lot2 = next(lot for lot in result["tender"]["lots"] if lot["id"] == "LOT-0002")

    assert (
        "noAccessibilityCriteriaRationale" in lot1
    ), "Expected noAccessibilityCriteriaRationale for LOT-0001"
    assert (
        lot1["noAccessibilityCriteriaRationale"]
        == "Accessibility criteria are not included because of specific technical requirements."
    ), "Unexpected noAccessibilityCriteriaRationale content for LOT-0001"

    assert (
        "noAccessibilityCriteriaRationale" not in lot2
    ), "Did not expect noAccessibilityCriteriaRationale for LOT-0002"

    # Additional assertions to check integration with BT-754-Lot
    assert (
        lot1["hasAccessibilityCriteria"] is False
    ), "Expected hasAccessibilityCriteria to be False for LOT-0001"
    assert (
        lot2["hasAccessibilityCriteria"] is True
    ), "Expected hasAccessibilityCriteria to be True for LOT-0002"


if __name__ == "__main__":
    pytest.main()
