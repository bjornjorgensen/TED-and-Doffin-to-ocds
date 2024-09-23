# tests/test_bt_727_part.py

import pytest
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.ted_and_doffin_to_ocds.main import main


def test_bt_727_part_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="part">PART-0001</cbc:ID>
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
    xml_file = tmp_path / "test_input_part_place_performance.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open("output.json") as f:
        result = json.load(f)

    assert "tender" in result, "Expected 'tender' in result"
    assert (
        "deliveryLocations" in result["tender"]
    ), "Expected 'deliveryLocations' in tender"
    assert (
        len(result["tender"]["deliveryLocations"]) == 1
    ), f"Expected 1 delivery location, got {len(result['tender']['deliveryLocations'])}"
    assert (
        result["tender"]["deliveryLocations"][0]["description"]
        == "Anywhere in the European Economic Area"
    ), f"Expected description 'Anywhere in the European Economic Area', got {result['tender']['deliveryLocations'][0]['description']}"


if __name__ == "__main__":
    pytest.main()
