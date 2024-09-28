# tests/test_bt_727_Lot.py
from pathlib import Path
import pytest
import json
import sys

# Add the parent directory to sys.path to import main
sys.path.append(str(Path(__file__).parent.parent))
from src.ted_and_doffin_to_ocds.main import main


def test_bt_727_lot_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:ProcurementProject>
                <cac:RealizedLocation>
                    <cac:Address>
                        <cbc:Region>anyw-eea</cbc:Region>
                    </cac:Address>
                </cac:RealizedLocation>
            </cac:ProcurementProject>
        </cac:ProcurementProjectLot>
    </root>
    """
    xml_file = tmp_path / "test_input_lot_place_performance.xml"
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
    assert (
        item["relatedLot"] == "LOT-0001"
    ), f"Expected related lot 'LOT-0001', got {item['relatedLot']}"
    assert "deliveryLocations" in item, "Expected 'deliveryLocations' in item"
    assert (
        len(item["deliveryLocations"]) == 1
    ), f"Expected 1 delivery location, got {len(item['deliveryLocations'])}"
    assert (
        item["deliveryLocations"][0]["description"]
        == "Anywhere in the European Economic Area"
    ), f"Expected description 'Anywhere in the European Economic Area', got {item['deliveryLocations'][0]['description']}"


if __name__ == "__main__":
    pytest.main()
