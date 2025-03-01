# tests/test_OPP_034_Tender.py
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


def test_opp_034_tender_integration(tmp_path, setup_logging, temp_output_dir) -> None:
    logger = setup_logging

    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
        xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
        xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
        xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
        xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
        xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1">
        <cbc:ID>notice-1</cbc:ID>
        <cbc:ContractFolderID>cf-1</cbc:ContractFolderID>
        <ext:UBLExtensions>
            <ext:UBLExtension>
                <ext:ExtensionContent>
                    <efext:EformsExtension>
                        <efac:NoticeResult>
                            <efac:LotResult>
                                <cbc:ID schemeName="result">RES-0001</cbc:ID>
                                <efac:LotTender>
                                    <cbc:ID schemeName="tender">TEN-0001</cbc:ID>
                                </efac:LotTender>
                                <efac:TenderLot>
                                    <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
                                </efac:TenderLot>
                            </efac:LotResult>
                            <efac:LotTender>
                                <cbc:ID schemeName="tender">TEN-0001</cbc:ID>
                                <efac:ContractTerm>
                                    <efac:FinancialPerformanceRequirement>
                                        <efbc:FinancialPerformanceTypeCode>penalty</efbc:FinancialPerformanceTypeCode>
                                        <efbc:FinancialPerformanceDescription>Penalty for late delivery</efbc:FinancialPerformanceDescription>
                                    </efac:FinancialPerformanceRequirement>
                                </efac:ContractTerm>
                                <efac:ContractTerm>
                                    <efac:FinancialPerformanceRequirement>
                                        <efbc:FinancialPerformanceTypeCode>reward</efbc:FinancialPerformanceTypeCode>
                                        <efbc:FinancialPerformanceDescription>Bonus for early completion</efbc:FinancialPerformanceDescription>
                                    </efac:FinancialPerformanceRequirement>
                                </efac:ContractTerm>
                            </efac:LotTender>
                        </efac:NoticeResult>
                    </efext:EformsExtension>
                </ext:ExtensionContent>
            </ext:UBLExtension>
        </ext:UBLExtensions>
    </ContractAwardNotice>
    """

    # Create input XML file
    xml_file = tmp_path / "test_input_penalties_and_rewards.xml"
    xml_file.write_text(xml_content)

    # Run main and get result
    result = run_main_and_get_result(xml_file, temp_output_dir)

    # logger.info("Test result: %s", json.dumps(result, indent=2) # Logging disabled)

    # Verify the results
    assert "tender" in result, "Expected 'tender' in result"
    assert "lots" in result["tender"], "Expected 'lots' in tender"
    assert (
        len(result["tender"]["lots"]) == 1
    ), f"Expected 1 lot, got {len(result['tender']['lots'])}"
    lot = result["tender"]["lots"][0]
    assert lot["id"] == "LOT-0001", f"Expected lot id 'LOT-0001', got {lot['id']}"
    assert "penaltiesAndRewards" in lot, "Expected 'penaltiesAndRewards' in lot"
    assert (
        "penalties" in lot["penaltiesAndRewards"]
    ), "Expected 'penalties' in penaltiesAndRewards"
    assert (
        "rewards" in lot["penaltiesAndRewards"]
    ), "Expected 'rewards' in penaltiesAndRewards"
    assert lot["penaltiesAndRewards"]["penalties"] == [
        "Penalty for late delivery"
    ], "Unexpected penalties"
    assert lot["penaltiesAndRewards"]["rewards"] == [
        "Bonus for early completion"
    ], "Unexpected rewards"


if __name__ == "__main__":
    pytest.main(["-v"])
