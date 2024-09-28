# tests/test_bt_7531_Lot.py
from pathlib import Path
import pytest
import json
import sys

# Add the parent directory to sys.path to import main
sys.path.append(str(Path(__file__).parent.parent))
from src.ted_and_doffin_to_ocds.main import main


def test_bt_7531_lot_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
          xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
          xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:TenderingTerms>
                <ext:UBLExtensions>
                    <ext:UBLExtension>
                        <ext:ExtensionContent>
                            <efext:EformsExtension>
                                <efac:SelectionCriteria>
                                    <cbc:CalculationExpressionCode listName="usage">used</cbc:CalculationExpressionCode>
                                    <efac:CriterionParameter>
                                        <efbc:ParameterCode listName="number-weight">per-exa</efbc:ParameterCode>
                                    </efac:CriterionParameter>
                                </efac:SelectionCriteria>
                            </efext:EformsExtension>
                        </ext:ExtensionContent>
                    </ext:UBLExtension>
                </ext:UBLExtensions>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </root>
    """
    xml_file = tmp_path / "test_input_selection_criteria_number_weight.xml"
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
    assert "selectionCriteria" in lot, "Expected 'selectionCriteria' in lot"
    assert (
        "criteria" in lot["selectionCriteria"]
    ), "Expected 'criteria' in selectionCriteria"
    assert (
        len(lot["selectionCriteria"]["criteria"]) == 1
    ), f"Expected 1 criterion, got {len(lot['selectionCriteria']['criteria'])}"

    criterion = lot["selectionCriteria"]["criteria"][0]
    assert "numbers" in criterion, "Expected 'numbers' in criterion"
    assert (
        len(criterion["numbers"]) == 1
    ), f"Expected 1 number, got {len(criterion['numbers'])}"
    assert (
        criterion["numbers"][0]["weight"] == "percentageExact"
    ), f"Expected weight 'percentageExact', got {criterion['numbers'][0]['weight']}"


if __name__ == "__main__":
    pytest.main()
