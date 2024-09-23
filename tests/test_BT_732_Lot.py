# tests/test_bt_732_Lot.py

import pytest
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.ted_and_doffin_to_ocds.main import main


def test_bt_732_lot_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:TenderingTerms>
                <cac:SecurityClearanceTerm>
                    <cbc:Description languageID="ENG">EU Confidential security clearance of Key Management Personnel must be achieved before access to procurement documents be granted</cbc:Description>
                </cac:SecurityClearanceTerm>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </root>
    """
    xml_file = tmp_path / "test_input_lot_security_clearance_description.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open("output.json") as f:
        result = json.load(f)

    assert "tender" in result, "Expected 'tender' in result"
    assert "lots" in result["tender"], "Expected 'lots' in tender"
    assert (
        len(result["tender"]["lots"]) == 1
    ), f"Expected 1 lot, got {len(result['tender']['lots'])}"

    lot = result["tender"]["lots"][0]
    assert lot["id"] == "LOT-0001", f"Expected lot id 'LOT-0001', got {lot['id']}"
    assert "otherRequirements" in lot, "Expected 'otherRequirements' in lot"
    assert (
        "securityClearance" in lot["otherRequirements"]
    ), "Expected 'securityClearance' in otherRequirements"
    expected_description = "EU Confidential security clearance of Key Management Personnel must be achieved before access to procurement documents be granted"
    assert (
        lot["otherRequirements"]["securityClearance"] == expected_description
    ), f"Expected security clearance description '{expected_description}', got '{lot['otherRequirements']['securityClearance']}'"


if __name__ == "__main__":
    pytest.main()
