# tests/test_bt_728_procedure.py
from pathlib import Path
import pytest
import json
import sys

# Add the parent directory to sys.path to import main
sys.path.append(str(Path(__file__).parent.parent))
from src.ted_and_doffin_to_ocds.main import main


def test_bt_728_procedure_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProject>
            <cac:RealizedLocation>
                <cbc:Description languageID="ENG">Further realizations ...</cbc:Description>
            </cac:RealizedLocation>
        </cac:ProcurementProject>
    </root>
    """
    xml_file = tmp_path / "test_input_procedure_place_performance_additional.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with Path("output.json").open() as f:
        result = json.load(f)

    assert "tender" in result, "Expected 'tender' in result"
    assert (
        "deliveryAddresses" in result["tender"]
    ), "Expected 'deliveryAddresses' in tender"
    assert (
        len(result["tender"]["deliveryAddresses"]) == 1
    ), f"Expected 1 delivery address, got {len(result['tender']['deliveryAddresses'])}"
    assert (
        result["tender"]["deliveryAddresses"][0]["description"]
        == "Further realizations ..."
    ), f"Expected description 'Further realizations ...', got {result['tender']['deliveryAddresses'][0]['description']}"


if __name__ == "__main__":
    pytest.main()