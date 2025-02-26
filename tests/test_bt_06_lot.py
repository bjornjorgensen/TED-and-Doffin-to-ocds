# tests/test_bt_06_Lot.py

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


def test_bt_06_lot_integration(tmp_path, setup_logging, temp_output_dir) -> None:
    logger = setup_logging

    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
        xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
        xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cbc:ID>notice-1</cbc:ID>
        <cbc:ContractFolderID>cf-1</cbc:ContractFolderID>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:ProcurementProject>
                <cac:ProcurementAdditionalType>
                    <cbc:ProcurementTypeCode listName="strategic-procurement">inn-pur</cbc:ProcurementTypeCode>
                </cac:ProcurementAdditionalType>
            </cac:ProcurementProject>
        </cac:ProcurementProjectLot>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0002</cbc:ID>
            <cac:ProcurementProject>
                <cac:ProcurementAdditionalType>
                    <cbc:ProcurementTypeCode listName="strategic-procurement">env-imp</cbc:ProcurementTypeCode>
                </cac:ProcurementAdditionalType>
            </cac:ProcurementProject>
        </cac:ProcurementProjectLot>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0003</cbc:ID>
            <cac:ProcurementProject>
                <cac:ProcurementAdditionalType>
                    <cbc:ProcurementTypeCode listName="strategic-procurement">none</cbc:ProcurementTypeCode>
                </cac:ProcurementAdditionalType>
            </cac:ProcurementProject>
        </cac:ProcurementProjectLot>
    </ContractAwardNotice>
    """

    # Create input XML file
    xml_file = tmp_path / "test_input_strategic_procurement.xml"
    xml_file.write_text(xml_content)

    # Run main and get result
    result = run_main_and_get_result(xml_file, temp_output_dir)

    # logger.info("Test result: %s", json.dumps(result, indent=2) # Logging disabled)

    # Verify the results
    assert "tender" in result, "Expected 'tender' in result"
    assert "lots" in result["tender"], "Expected 'lots' in result['tender']"
    assert (
        len(result["tender"]["lots"]) == 3
    ), f"Expected 3 lots, got {len(result['tender']['lots'])}"

    lot_1 = next(lot for lot in result["tender"]["lots"] if lot["id"] == "LOT-0001")
    assert (
        lot_1["hasSustainability"] is True
    ), "Expected LOT-0001 to have sustainability"
    assert (
        len(lot_1["sustainability"]) == 1
    ), f"Expected 1 sustainability entry for LOT-0001, got {len(lot_1['sustainability'])}"
    assert (
        lot_1["sustainability"][0]["goal"] == "economic.innovativePurchase"
    ), f"Expected goal 'economic.innovativePurchase' for LOT-0001, got {lot_1['sustainability'][0]['goal']}"
    assert (
        sorted(lot_1["sustainability"][0]["strategies"]) == sorted([
            "awardCriteria", 
            "contractPerformanceConditions", 
            "selectionCriteria", 
            "technicalSpecifications"
        ])
    ), "Expected all four strategies for LOT-0001"

    lot_2 = next(lot for lot in result["tender"]["lots"] if lot["id"] == "LOT-0002")
    assert (
        lot_2["hasSustainability"] is True
    ), "Expected LOT-0002 to have sustainability"
    assert (
        len(lot_2["sustainability"]) == 1
    ), f"Expected 1 sustainability entry for LOT-0002, got {len(lot_2['sustainability'])}"
    assert (
        lot_2["sustainability"][0]["goal"] == "environmental"
    ), f"Expected goal 'environmental' for LOT-0002, got {lot_2['sustainability'][0]['goal']}"
    assert (
        sorted(lot_2["sustainability"][0]["strategies"]) == sorted([
            "awardCriteria", 
            "contractPerformanceConditions", 
            "selectionCriteria", 
            "technicalSpecifications"
        ])
    ), "Expected all four strategies for LOT-0002"

    lot_3 = next(lot for lot in result["tender"]["lots"] if lot["id"] == "LOT-0003")
    assert (
        "hasSustainability" not in lot_3
    ), "Expected LOT-0003 to not have sustainability information"
    assert (
        "sustainability" not in lot_3
    ), "Expected LOT-0003 to not have sustainability information"


if __name__ == "__main__":
    pytest.main(["-v"])
