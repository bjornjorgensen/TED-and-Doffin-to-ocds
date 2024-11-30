# tests/test_bt_750_lot.py
import json
import logging
import sys
import tempfile
from pathlib import Path

import pytest

# Add the parent directory to sys.path to import main
sys.path.append(str(Path(__file__).parent.parent))
from src.ted_and_doffin_to_ocds.main import configure_logging, main


@pytest.fixture(scope="module")
def setup_logging():
    configure_logging()
    return logging.getLogger(__name__)


@pytest.fixture
def temp_output_dir():
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield Path(tmpdirname)


def run_main_and_get_result(xml_file, output_dir):
    main(str(xml_file), str(output_dir), "ocds-test-prefix", "test-scheme")
    output_files = list(output_dir.glob("*_release_0.json"))
    assert len(output_files) == 1, f"Expected 1 output file, got {len(output_files)}"
    with output_files[0].open() as f:
        return json.load(f)


def test_bt_750_lot_integration(tmp_path, setup_logging, temp_output_dir) -> None:
    logger = setup_logging

    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractAwardNotice xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
                          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
                          xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
                          xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
                          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
                          xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1">
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
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:TenderingTerms>
                <ext:UBLExtensions>
                    <ext:UBLExtension>
                        <ext:ExtensionContent>
                            <efext:EformsExtension>
                                <efac:SelectionCriteria>
                                    <cbc:Description languageID="ENG">Turnover over contract value rate</cbc:Description>
                                </efac:SelectionCriteria>
                            </efext:EformsExtension>
                        </ext:ExtensionContent>
                    </ext:UBLExtension>
                </ext:UBLExtensions>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </ContractAwardNotice>
    """
    xml_file = tmp_path / "test_input_selection_criteria.xml"
    xml_file.write_text(xml_content)

    # Run main and get result
    result = run_main_and_get_result(xml_file, temp_output_dir)
    logger.info("Result: %s", json.dumps(result, indent=2))

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
        len(lot["selectionCriteria"]["criteria"]) == 2
    ), f"Expected 2 criteria, got {len(lot['selectionCriteria']['criteria'])}"

    criterion_1 = lot["selectionCriteria"]["criteria"][0]
    expected_description_1 = "Minimum Turnover: Turnover over contract value rate"
    assert (
        criterion_1["description"] == expected_description_1
    ), f"Expected description '{expected_description_1}', got '{criterion_1['description']}'"

    criterion_2 = lot["selectionCriteria"]["criteria"][1]
    expected_description_2 = "Turnover over contract value rate"
    assert (
        criterion_2["description"] == expected_description_2
    ), f"Expected description '{expected_description_2}', got '{criterion_2['description']}'"

    logger.info("Test bt_750_lot_integration passed successfully.")


if __name__ == "__main__":
    pytest.main(["-v", "-s"])
