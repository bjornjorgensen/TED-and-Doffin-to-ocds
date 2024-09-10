# tests/test_BT_750_Lot.py

import pytest
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.ted_and_doffin_to_ocds.main import main


def test_bt_750_lot_integration(tmp_path):
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
                                <efac:SelectionCriteria>
                                    <cbc:CalculationExpressionCode listName="usage">used</cbc:CalculationExpressionCode>
                                    <cbc:Name>Minimum Turnover</cbc:Name>
                                    <cbc:Description languageID="ENG">Turnover over contract value rate</cbc:Description>
                                </efac:SelectionCriteria>
                            </efext:EformsExtension>
                        </ext:ExtensionContent>
                    </ext:UBLExtension>
                </ext:UBLExtensions>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </root>
    """
    xml_file = tmp_path / "test_input_selection_criteria.xml"
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
    assert "selectionCriteria" in lot, "Expected 'selectionCriteria' in lot"
    assert (
        "criteria" in lot["selectionCriteria"]
    ), "Expected 'criteria' in selectionCriteria"
    assert (
        len(lot["selectionCriteria"]["criteria"]) == 1
    ), f"Expected 1 criterion, got {len(lot['selectionCriteria']['criteria'])}"

    criterion = lot["selectionCriteria"]["criteria"][0]
    expected_description = "Minimum Turnover: Turnover over contract value rate"
    assert (
        criterion["description"] == expected_description
    ), f"Expected description '{expected_description}', got '{criterion['description']}'"


if __name__ == "__main__":
    pytest.main()
