# tests/test_BT_7220_Lot.py

import pytest
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main


def test_bt_7220_lot_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
          xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:TenderingTerms>
                <ext:UBLExtensions>
                    <ext:UBLExtension>
                        <ext:ExtensionContent>
                            <efext:EformsExtension>
                                <efac:Funding>
                                    <cbc:FundingProgramCode listName="eu-programme">ERDF_2021</cbc:FundingProgramCode>
                                </efac:Funding>
                            </efext:EformsExtension>
                        </ext:ExtensionContent>
                    </ext:UBLExtension>
                </ext:UBLExtensions>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </root>
    """
    xml_file = tmp_path / "test_input_lot_eu_funds.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open("output.json", "r") as f:
        result = json.load(f)

    assert "lots" in result, "Expected 'lots' in result"
    assert len(result["lots"]) == 1, f"Expected 1 lot, got {len(result['lots'])}"

    lot = result["lots"][0]
    assert lot["id"] == "LOT-0001", f"Expected lot id 'LOT-0001', got {lot['id']}"
    assert "planning" in lot, "Expected 'planning' in lot"
    assert "budget" in lot["planning"], "Expected 'budget' in lot planning"
    assert "finance" in lot["planning"]["budget"], "Expected 'finance' in lot budget"
    assert (
        len(lot["planning"]["budget"]["finance"]) == 1
    ), f"Expected 1 finance object, got {len(lot['planning']['budget']['finance'])}"
    finance = lot["planning"]["budget"]["finance"][0]
    assert finance["id"] == "1", f"Expected finance id '1', got {finance['id']}"
    assert (
        finance["title"] == "ERDF_2021"
    ), f"Expected finance title 'ERDF_2021', got {finance['title']}"


if __name__ == "__main__":
    pytest.main()
