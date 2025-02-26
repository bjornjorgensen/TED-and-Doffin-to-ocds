# tests/test_bt_76_Lot.py
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
    output_files = list(output_dir.glob("*.json"))
    assert len(output_files) == 1, f"Expected 1 output file, got {len(output_files)}"
    with output_files[0].open() as f:
        return json.load(f)


def test_bt_76_lot_integration(tmp_path, setup_logging, temp_output_dir) -> None:
    logger = setup_logging

    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
        xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
        xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cbc:ID>notice-1</cbc:ID>
        <cbc:ContractFolderID>cf-1</cbc:ContractFolderID>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:TenderingTerms>
                <cac:TendererQualificationRequest>
                    <cbc:companyLegalForm languageID="ENG">The tenderer must be a registered company</cbc:companyLegalForm>
                </cac:TendererQualificationRequest>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0002</cbc:ID>
            <cac:TenderingTerms>
                <cac:TendererQualificationRequest>
                    <cbc:companyLegalForm languageID="ENG">The tenderer must be a partnership</cbc:companyLegalForm>
                </cac:TendererQualificationRequest>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </ContractAwardNotice>
    """

    # Create input XML file
    xml_file = tmp_path / "test_input_tenderer_legal_form.xml"
    xml_file.write_text(xml_content)

    # Run main and get result
    result = run_main_and_get_result(xml_file, temp_output_dir)
    # logger.info("Result: %s", json.dumps(result, indent=2) # Logging disabled)

    # Verify the results
    assert "tender" in result, "Expected 'tender' in result"
    assert "lots" in result["tender"], "Expected 'lots' in tender"
    assert (
        len(result["tender"]["lots"]) == 2
    ), f"Expected 2 lots, got {len(result['tender']['lots'])}"

    lot1 = next(lot for lot in result["tender"]["lots"] if lot["id"] == "LOT-0001")
    lot2 = next(lot for lot in result["tender"]["lots"] if lot["id"] == "LOT-0002")

    assert "contractTerms" in lot1, "Expected 'contractTerms' in LOT-0001"
    assert (
        "tendererLegalForm" in lot1["contractTerms"]
    ), "Expected 'tendererLegalForm' in LOT-0001 contractTerms"
    assert (
        lot1["contractTerms"]["tendererLegalForm"]
        == "The tenderer must be a registered company"
    ), "Unexpected tendererLegalForm content for LOT-0001"

    assert "contractTerms" in lot2, "Expected 'contractTerms' in LOT-0002"
    assert (
        "tendererLegalForm" in lot2["contractTerms"]
    ), "Expected 'tendererLegalForm' in LOT-0002 contractTerms"
    assert (
        lot2["contractTerms"]["tendererLegalForm"]
        == "The tenderer must be a partnership"
    ), "Unexpected tendererLegalForm content for LOT-0002"


def test_bt_76_lot_missing_company_legal_form(
    tmp_path, setup_logging, temp_output_dir
) -> None:
    logger = setup_logging

    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
        xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
        xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cbc:ID>notice-1</cbc:ID>
        <cbc:ContractFolderID>cf-1</cbc:ContractFolderID>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:TenderingTerms>
                <cac:TendererQualificationRequest>
                    <!-- companyLegalForm is missing -->
                </cac:TendererQualificationRequest>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </ContractAwardNotice>
    """

    # Create input XML file
    xml_file = tmp_path / "test_input_missing_company_legal_form.xml"
    xml_file.write_text(xml_content)

    # Run main and get result
    result = run_main_and_get_result(xml_file, temp_output_dir)
    # logger.info("Result: %s", json.dumps(result, indent=2) # Logging disabled)

    # Verify the results
    assert "tender" in result, "Expected 'tender' in result"
    assert "lots" in result["tender"], "Expected 'lots' in tender"
    assert (
        len(result["tender"]["lots"]) == 1
    ), f"Expected 1 lot, got {len(result['tender']['lots'])}"

    lot = result["tender"]["lots"][0]
    assert lot["id"] == "LOT-0001", "Expected lot id 'LOT-0001'"
    assert "contractTerms" not in lot or "tendererLegalForm" not in lot.get(
        "contractTerms", {}
    ), "Did not expect 'tendererLegalForm' when companyLegalForm is missing"


def test_bt_76_lot_empty_company_legal_form(
    tmp_path, setup_logging, temp_output_dir
) -> None:
    logger = setup_logging

    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
        xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
        xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cbc:ID>notice-1</cbc:ID>
        <cbc:ContractFolderID>cf-1</cbc:ContractFolderID>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:TenderingTerms>
                <cac:TendererQualificationRequest>
                    <cbc:companyLegalForm languageID="ENG"></cbc:companyLegalForm>
                </cac:TendererQualificationRequest>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </ContractAwardNotice>
    """

    # Create input XML file
    xml_file = tmp_path / "test_input_empty_company_legal_form.xml"
    xml_file.write_text(xml_content)

    # Run main and get result
    result = run_main_and_get_result(xml_file, temp_output_dir)
    # logger.info("Result: %s", json.dumps(result, indent=2) # Logging disabled)

    # Verify the results
    assert "tender" in result, "Expected 'tender' in result"
    assert "lots" in result["tender"], "Expected 'lots' in tender"
    assert (
        len(result["tender"]["lots"]) == 1
    ), f"Expected 1 lot, got {len(result['tender']['lots'])}"

    lot = result["tender"]["lots"][0]
    assert lot["id"] == "LOT-0001", "Expected lot id 'LOT-0001'"
    assert "contractTerms" not in lot or "tendererLegalForm" not in lot.get(
        "contractTerms", {}
    ), "Did not expect 'tendererLegalForm' when companyLegalForm is empty"


def test_bt_76_lot_multiple_qualification_requests(
    tmp_path, setup_logging, temp_output_dir
) -> None:
    logger = setup_logging

    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
        xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
        xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cbc:ID>notice-1</cbc:ID>
        <cbc:ContractFolderID>cf-1</cbc:ContractFolderID>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:TenderingTerms>
                <cac:TendererQualificationRequest>
                    <cbc:companyLegalForm languageID="ENG">First legal form requirement</cbc:companyLegalForm>
                </cac:TendererQualificationRequest>
                <cac:TendererQualificationRequest>
                    <cbc:companyLegalForm languageID="ENG">Second legal form requirement</cbc:companyLegalForm>
                </cac:TendererQualificationRequest>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </ContractAwardNotice>
    """

    # Create input XML file
    xml_file = tmp_path / "test_input_multiple_qualification_requests.xml"
    xml_file.write_text(xml_content)

    # Run main and get result
    result = run_main_and_get_result(xml_file, temp_output_dir)
    # logger.info("Result: %s", json.dumps(result, indent=2) # Logging disabled)

    # Verify the results
    assert "tender" in result, "Expected 'tender' in result"
    assert "lots" in result["tender"], "Expected 'lots' in tender"
    assert (
        len(result["tender"]["lots"]) == 1
    ), f"Expected 1 lot, got {len(result['tender']['lots'])}"

    lot = result["tender"]["lots"][0]
    assert lot["id"] == "LOT-0001", "Expected lot id 'LOT-0001'"
    assert "contractTerms" in lot, "Expected 'contractTerms' in lot"
    assert (
        "tendererLegalForm" in lot["contractTerms"]
    ), "Expected 'tendererLegalForm' in lot contractTerms"
    assert lot["contractTerms"]["tendererLegalForm"] in [
        "First legal form requirement",
        "Second legal form requirement",
    ], "Unexpected tendererLegalForm content"


if __name__ == "__main__":
    pytest.main(["-v", "-s"])
