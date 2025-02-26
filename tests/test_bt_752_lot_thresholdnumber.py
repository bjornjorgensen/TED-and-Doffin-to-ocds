# tests/test_bt_752_lot_thresholdnumber.py
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
    # Logging disabled for tests
    logger = logging.getLogger(__name__)
    logger.disabled = True
    return logger


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


def test_bt_752_lot_threshold_number_integration(
    tmp_path, setup_logging, temp_output_dir
) -> None:
    logger = setup_logging

    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractAwardNotice xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
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
                                        <efbc:ParameterCode listName="number-threshold"/>
                                        <efbc:ParameterNumeric>3.5</efbc:ParameterNumeric>
                                    </efac:CriterionParameter>
                                </efac:SelectionCriteria>
                            </efext:EformsExtension>
                        </ext:ExtensionContent>
                    </ext:UBLExtension>
                </ext:UBLExtensions>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0002</cbc:ID>
            <cac:TenderingTerms>
                <ext:UBLExtensions>
                    <ext:UBLExtension>
                        <ext:ExtensionContent>
                            <efext:EformsExtension>
                                <efac:SelectionCriteria>
                                    <cbc:CalculationExpressionCode listName="usage">not-used</cbc:CalculationExpressionCode>
                                    <efac:CriterionParameter>
                                        <efbc:ParameterCode listName="number-threshold"/>
                                        <efbc:ParameterNumeric>2.5</efbc:ParameterNumeric>
                                    </efac:CriterionParameter>
                                </efac:SelectionCriteria>
                            </efext:EformsExtension>
                        </ext:ExtensionContent>
                    </ext:UBLExtension>
                </ext:UBLExtensions>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </ContractAwardNotice>
    """

    xml_file = tmp_path / "test_input_selection_criteria_threshold_number.xml"
    xml_file.write_text(xml_content)

    result = run_main_and_get_result(xml_file, temp_output_dir)
    # logger.info("Result: %s", json.dumps(result, indent=2) # Logging disabled)

    # Verify basic structure
    assert "tender" in result
    assert "lots" in result["tender"]

    # Find lots with selection criteria
    lots_with_criteria = [
        lot
        for lot in result["tender"]["lots"]
        if "selectionCriteria" in lot and lot["selectionCriteria"].get("criteria")
    ]

    # Should only have selection criteria for LOT-0001
    assert len(lots_with_criteria) == 1
    lot = lots_with_criteria[0]
    assert lot["id"] == "LOT-0001"

    criteria = lot["selectionCriteria"]["criteria"]
    assert len(criteria) == 1

    criterion = criteria[0]
    assert "numbers" in criterion
    assert len(criterion["numbers"]) == 1
    assert criterion["numbers"][0]["number"] == 3.5

    # Verify LOT-0002 exists but has no selection criteria
    lot2 = next(lot for lot in result["tender"]["lots"] if lot["id"] == "LOT-0002")
    assert "selectionCriteria" not in lot2 or not lot2["selectionCriteria"].get(
        "criteria"
    )

    # logger.info("Test bt_752_lot_threshold_number_integration passed successfully.") # Logging disabled


def test_bt_752_no_threshold_number(tmp_path, temp_output_dir) -> None:
    """Test case when no threshold numbers are present"""
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractAwardNotice xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
                         xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
        </cac:ProcurementProjectLot>
    </ContractAwardNotice>
    """

    xml_file = tmp_path / "test_input_no_threshold.xml"
    xml_file.write_text(xml_content)

    result = run_main_and_get_result(xml_file, temp_output_dir)

    # Verify the output doesn't contain selection criteria
    assert "tender" in result
    assert "lots" in result["tender"]
    lot = next(
        (lot for lot in result["tender"]["lots"] if lot["id"] == "LOT-0001"), None
    )
    assert lot is not None
    assert "selectionCriteria" not in lot


if __name__ == "__main__":
    pytest.main(["-v", "-s"])
