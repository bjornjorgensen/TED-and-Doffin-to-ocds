# tests/test_bt_726_LotsGroup.py
from pathlib import Path
import pytest
import json
import sys

# Add the parent directory to sys.path to import main
sys.path.append(str(Path(__file__).parent.parent))
from src.ted_and_doffin_to_ocds.main import main


def test_bt_726_lots_group_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="LotsGroup">GLO-0001</cbc:ID>
            <cac:ProcurementProject>
                <cbc:SMESuitableIndicator>true</cbc:SMESuitableIndicator>
            </cac:ProcurementProject>
        </cac:ProcurementProjectLot>
    </root>
    """
    xml_file = tmp_path / "test_input_lots_group_sme_suitability.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with Path("output.json").open() as f:
        result = json.load(f)

    assert "tender" in result, "Expected 'tender' in result"
    assert "lotGroups" in result["tender"], "Expected 'lotGroups' in tender"
    assert (
        len(result["tender"]["lotGroups"]) == 1
    ), f"Expected 1 lot group, got {len(result['tender']['lotGroups'])}"

    lot_group = result["tender"]["lotGroups"][0]
    assert (
        lot_group["id"] == "GLO-0001"
    ), f"Expected lot group id 'GLO-0001', got {lot_group['id']}"
    assert "suitability" in lot_group, "Expected 'suitability' in lot group"
    assert "sme" in lot_group["suitability"], "Expected 'sme' in lot group suitability"
    assert (
        lot_group["suitability"]["sme"] is True
    ), f"Expected SME suitability to be True, got {lot_group['suitability']['sme']}"


if __name__ == "__main__":
    pytest.main()