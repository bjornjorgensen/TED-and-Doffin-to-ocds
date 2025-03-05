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
    """
    Test BT-752 Lot Threshold Number mapping.
    
    Verifies that numeric threshold values from selection criteria are correctly:
    - Included in the OCDS output regardless of 'used' or 'not-used' marking
    - Mapped to the correct lot's selectionCriteria.criteria.numbers array
    """
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
                                    <efbc:ID>criterion-1</efbc:ID>
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
                                    <efbc:ID>criterion-2</efbc:ID>
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

    # Should have selection criteria for both lots now
    assert len(lots_with_criteria) == 2
    
    # Find LOT-0001
    lot1 = next(lot for lot in lots_with_criteria if lot["id"] == "LOT-0001")
    criteria1 = lot1["selectionCriteria"]["criteria"]
    assert len(criteria1) == 1
    criterion1 = criteria1[0]
    assert "numbers" in criterion1
    assert len(criterion1["numbers"]) == 1
    assert criterion1["numbers"][0]["number"] == 3.5

    # Verify LOT-0002 now has selection criteria with the not-used criterion
    lot2 = next(lot for lot in lots_with_criteria if lot["id"] == "LOT-0002")
    assert "selectionCriteria" in lot2
    criteria2 = lot2["selectionCriteria"]["criteria"]
    assert len(criteria2) == 1
    criterion2 = criteria2[0]
    assert "numbers" in criterion2
    assert len(criterion2["numbers"]) == 1
    assert criterion2["numbers"][0]["number"] == 2.5


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


def test_bt_752_missing_usage_attribute(tmp_path, temp_output_dir) -> None:
    """Test case when the usage attribute is missing - should include the criteria by default"""
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
                                    <!-- No usage code provided -->
                                    <efbc:ID>criterion-1</efbc:ID>
                                    <efac:CriterionParameter>
                                        <efbc:ParameterCode listName="number-threshold"/>
                                        <efbc:ParameterNumeric>4.2</efbc:ParameterNumeric>
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

    xml_file = tmp_path / "test_input_missing_usage.xml"
    xml_file.write_text(xml_content)

    result = run_main_and_get_result(xml_file, temp_output_dir)

    # Verify the output contains selection criteria despite missing usage attribute
    assert "tender" in result
    assert "lots" in result["tender"]
    lot = next(
        (lot for lot in result["tender"]["lots"] if lot["id"] == "LOT-0001"), None
    )
    assert lot is not None
    assert "selectionCriteria" in lot
    assert "criteria" in lot["selectionCriteria"]
    assert len(lot["selectionCriteria"]["criteria"]) == 1
    assert "numbers" in lot["selectionCriteria"]["criteria"][0]
    assert lot["selectionCriteria"]["criteria"][0]["numbers"][0]["number"] == 4.2


def test_bt_752_mixed_usage_in_one_lot(tmp_path, temp_output_dir) -> None:
    """Test case with multiple criteria in one lot with different usage values.
    All criteria should be included regardless of usage marking."""
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
                                <!-- First criterion: used -->
                                <efac:SelectionCriteria>
                                    <cbc:CalculationExpressionCode listName="usage">used</cbc:CalculationExpressionCode>
                                    <efbc:ID>criterion-1</efbc:ID>
                                    <efac:CriterionParameter>
                                        <efbc:ParameterCode listName="number-threshold"/>
                                        <efbc:ParameterNumeric>1.5</efbc:ParameterNumeric>
                                    </efac:CriterionParameter>
                                </efac:SelectionCriteria>
                                <!-- Second criterion: not-used -->
                                <efac:SelectionCriteria>
                                    <cbc:CalculationExpressionCode listName="usage">not-used</cbc:CalculationExpressionCode>
                                    <efbc:ID>criterion-2</efbc:ID>
                                    <efac:CriterionParameter>
                                        <efbc:ParameterCode listName="number-threshold"/>
                                        <efbc:ParameterNumeric>2.5</efbc:ParameterNumeric>
                                    </efac:CriterionParameter>
                                </efac:SelectionCriteria>
                                <!-- Third criterion: no usage specified -->
                                <efac:SelectionCriteria>
                                    <efbc:ID>criterion-3</efbc:ID>
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
    </ContractAwardNotice>
    """

    xml_file = tmp_path / "test_input_mixed_usage.xml"
    xml_file.write_text(xml_content)

    result = run_main_and_get_result(xml_file, temp_output_dir)

    # Verify the output contains all criteria regardless of usage
    assert "tender" in result
    assert "lots" in result["tender"]
    lot = next(
        (lot for lot in result["tender"]["lots"] if lot["id"] == "LOT-0001"), None
    )
    assert lot is not None
    assert "selectionCriteria" in lot
    assert "criteria" in lot["selectionCriteria"]
    
    # We should have exactly 3 criteria (all of them)
    assert len(lot["selectionCriteria"]["criteria"]) == 3
    
    # Get the criteria by ID
    criteria_by_id = {c.get("id"): c for c in lot["selectionCriteria"]["criteria"]}
    
    # Criterion 1 (used) should be present
    assert "criterion-1" in criteria_by_id
    assert criteria_by_id["criterion-1"]["numbers"][0]["number"] == 1.5
    
    # Criterion 2 (not-used) should also be present
    assert "criterion-2" in criteria_by_id
    assert criteria_by_id["criterion-2"]["numbers"][0]["number"] == 2.5
    
    # Criterion 3 (unspecified) should be present
    assert "criterion-3" in criteria_by_id
    assert criteria_by_id["criterion-3"]["numbers"][0]["number"] == 3.5


if __name__ == "__main__":
    pytest.main(["-v", "-s"])
