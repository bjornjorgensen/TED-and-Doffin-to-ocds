# tests/test_bt_625_Lot.py
from pathlib import Path
import pytest
import json
import sys

# Add the parent directory to sys.path to import main
sys.path.append(str(Path(__file__).parent.parent))
from src.ted_and_doffin_to_ocds.main import main


def test_bt_625_lot_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:ProcurementProject>
                <cbc:EstimatedOverallContractQuantity unitCode="TNE">45000</cbc:EstimatedOverallContractQuantity>
            </cac:ProcurementProject>
        </cac:ProcurementProjectLot>
    </root>
    """
    xml_file = tmp_path / "test_input_unit.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with Path("output.json").open() as f:
        result = json.load(f)

    assert "tender" in result, "Expected 'tender' in result"
    assert "items" in result["tender"], "Expected 'items' in tender"
    assert (
        len(result["tender"]["items"]) == 1
    ), f"Expected 1 item, got {len(result['tender']['items'])}"

    item = result["tender"]["items"][0]
    assert item["id"] == "1", f"Expected item id '1', got {item['id']}"
    assert "unit" in item, "Expected 'unit' in item"
    assert (
        item["unit"]["id"] == "TNE"
    ), f"Expected unit id 'TNE', got {item['unit']['id']}"
    assert (
        item["unit"]["scheme"] == "EU Measurement unit"
    ), f"Expected scheme 'EU Measurement unit', got {item['unit']['scheme']}"
    assert (
        item["unit"]["name"] == "tonne"
    ), f"Expected unit name 'tonne', got {item['unit']['name']}"
    assert (
        item["relatedLot"] == "LOT-0001"
    ), f"Expected relatedLot 'LOT-0001', got {item['relatedLot']}"


if __name__ == "__main__":
    pytest.main()