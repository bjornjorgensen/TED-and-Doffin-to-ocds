# tests/test_bt_57_Lot.py
from pathlib import Path
import pytest
import json
import sys

# Add the parent directory to sys.path to import main
sys.path.append(str(Path(__file__).parent.parent))
from src.ted_and_doffin_to_ocds.main import main


def test_bt_57_lot_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:ProcurementProject>
                <cac:ContractExtension>
                    <cac:Renewal>
                        <cac:Period>
                            <cbc:Description languageID="ENG">The buyer reserves the right to ...</cbc:Description>
                        </cac:Period>
                    </cac:Renewal>
                </cac:ContractExtension>
            </cac:ProcurementProject>
        </cac:ProcurementProjectLot>
    </root>
    """
    xml_file = tmp_path / "test_input_renewal_description.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with Path("output.json").open() as f:
        result = json.load(f)

    assert "tender" in result, "Expected 'tender' in result"
    assert "lots" in result["tender"], "Expected 'lots' in tender"
    assert (
        len(result["tender"]["lots"]) == 1
    ), f"Expected 1 lot, got {len(result['tender']['lots'])}"

    lot = result["tender"]["lots"][0]
    assert lot["id"] == "LOT-0001", f"Expected lot id 'LOT-0001', got {lot['id']}"
    assert "renewal" in lot, "Expected 'renewal' in lot"
    assert "description" in lot["renewal"], "Expected 'description' in lot renewal"
    expected_description = "The buyer reserves the right to ..."
    assert (
        lot["renewal"]["description"] == expected_description
    ), f"Expected description '{expected_description}', got {lot['renewal']['description']}"


if __name__ == "__main__":
    pytest.main()