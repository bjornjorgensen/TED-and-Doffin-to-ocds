# tests/test_bt_1375_procedure.py
from pathlib import Path
import pytest
import json
import sys

# Add the parent directory to sys.path to import main
sys.path.append(str(Path(__file__).parent.parent))
from src.ted_and_doffin_to_ocds.main import main


def test_bt_1375_procedure_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:TenderingTerms>
            <cac:LotDistribution>
                <cac:LotsGroup>
                    <cbc:LotsGroupID schemeName="LotsGroup">GLO-0001</cbc:LotsGroupID>
                    <cac:ProcurementProjectLotReference>
                        <cbc:ID schemeName="Lot">LOT-0002</cbc:ID>
                    </cac:ProcurementProjectLotReference>
                </cac:LotsGroup>
            </cac:LotDistribution>
        </cac:TenderingTerms>
    </root>
    """
    xml_file = tmp_path / "test_input_group_lot_identifier.xml"
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
    assert "relatedLots" in lot_group, "Expected 'relatedLots' in lot group"
    assert (
        len(lot_group["relatedLots"]) == 1
    ), f"Expected 1 related lot, got {len(lot_group['relatedLots'])}"
    assert (
        lot_group["relatedLots"][0] == "LOT-0002"
    ), f"Expected related lot 'LOT-0002', got {lot_group['relatedLots'][0]}"


if __name__ == "__main__":
    pytest.main()
