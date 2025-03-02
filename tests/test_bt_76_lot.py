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
                    <cbc:CompanyLegalForm languageID="ENG">The tenderer must be a registered company</cbc:CompanyLegalForm>
                </cac:TendererQualificationRequest>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0002</cbc:ID>
            <cac:TenderingTerms>
                <cac:TendererQualificationRequest>
                    <cbc:CompanyLegalForm languageID="ENG">The tenderer must be a partnership</cbc:CompanyLegalForm>
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
    # Check for multilingual structure since languageID is provided
    assert isinstance(lot1["contractTerms"]["tendererLegalForm"], dict), "Expected tendererLegalForm to be a dict with language keys"
    assert "ENG" in lot1["contractTerms"]["tendererLegalForm"], "Expected 'ENG' key in tendererLegalForm"
    assert (
        lot1["contractTerms"]["tendererLegalForm"]["ENG"]
        == "The tenderer must be a registered company"
    ), "Unexpected tendererLegalForm content for LOT-0001"

    assert "contractTerms" in lot2, "Expected 'contractTerms' in LOT-0002"
    assert (
        "tendererLegalForm" in lot2["contractTerms"]
    ), "Expected 'tendererLegalForm' in LOT-0002 contractTerms"
    assert isinstance(lot2["contractTerms"]["tendererLegalForm"], dict), "Expected tendererLegalForm to be a dict with language keys"
    assert "ENG" in lot2["contractTerms"]["tendererLegalForm"], "Expected 'ENG' key in tendererLegalForm"
    assert (
        lot2["contractTerms"]["tendererLegalForm"]["ENG"]
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
                    <!-- CompanyLegalForm is missing -->
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
    ), "Did not expect 'tendererLegalForm' when CompanyLegalForm is missing"


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
                    <cbc:CompanyLegalForm languageID="ENG"></cbc:CompanyLegalForm>
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
    ), "Did not expect 'tendererLegalForm' when CompanyLegalForm is empty"


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
                    <cbc:CompanyLegalForm languageID="ENG">First legal form requirement</cbc:CompanyLegalForm>
                </cac:TendererQualificationRequest>
                <cac:TendererQualificationRequest>
                    <cbc:CompanyLegalForm languageID="ENG">Second legal form requirement</cbc:CompanyLegalForm>
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
    assert isinstance(lot["contractTerms"]["tendererLegalForm"], dict), "Expected tendererLegalForm to be a dict with language keys"
    assert "ENG" in lot["contractTerms"]["tendererLegalForm"], "Expected 'ENG' key in tendererLegalForm"


def test_bt_76_lot_multilingual_text(
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
                    <cbc:CompanyLegalForm languageID="ENG">The tenderer must be a registered company</cbc:CompanyLegalForm>
                    <cbc:CompanyLegalForm languageID="FRA">Le soumissionnaire doit être une société enregistrée</cbc:CompanyLegalForm>
                    <cbc:CompanyLegalForm languageID="NOR">Tilbyderen må være et registrert selskap</cbc:CompanyLegalForm>
                </cac:TendererQualificationRequest>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </ContractAwardNotice>
    """

    # Create input XML file
    xml_file = tmp_path / "test_input_multilingual_legal_form.xml"
    xml_file.write_text(xml_content)

    # Run main and get result
    result = run_main_and_get_result(xml_file, temp_output_dir)

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
    
    # Check multilingual structure
    assert isinstance(lot["contractTerms"]["tendererLegalForm"], dict), "Expected tendererLegalForm to be a dict with language keys"
    assert "ENG" in lot["contractTerms"]["tendererLegalForm"], "Expected 'ENG' key in tendererLegalForm"
    assert "FRA" in lot["contractTerms"]["tendererLegalForm"], "Expected 'FRA' key in tendererLegalForm"
    assert "NOR" in lot["contractTerms"]["tendererLegalForm"], "Expected 'NOR' key in tendererLegalForm"
    
    assert lot["contractTerms"]["tendererLegalForm"]["ENG"] == "The tenderer must be a registered company"
    assert lot["contractTerms"]["tendererLegalForm"]["FRA"] == "Le soumissionnaire doit être une société enregistrée"
    assert lot["contractTerms"]["tendererLegalForm"]["NOR"] == "Tilbyderen må være et registrert selskap"


def test_bt_76_lot_no_language_id(
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
                    <cbc:CompanyLegalForm>The tenderer must be a registered company</cbc:CompanyLegalForm>
                </cac:TendererQualificationRequest>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </ContractAwardNotice>
    """

    # Create input XML file
    xml_file = tmp_path / "test_input_no_language_id.xml"
    xml_file.write_text(xml_content)

    # Run main and get result
    result = run_main_and_get_result(xml_file, temp_output_dir)

    # Verify the results
    assert "tender" in result, "Expected 'tender' in result"
    assert "lots" in result["tender"], "Expected 'lots' in tender"
    
    lot = result["tender"]["lots"][0]
    assert lot["id"] == "LOT-0001", "Expected lot id 'LOT-0001'"
    assert "contractTerms" in lot, "Expected 'contractTerms' in lot"
    assert (
        "tendererLegalForm" in lot["contractTerms"]
    ), "Expected 'tendererLegalForm' in lot contractTerms"
    
    # Check that with no languageID, value is directly stored as a string
    assert isinstance(lot["contractTerms"]["tendererLegalForm"], str), "Expected tendererLegalForm to be a string when no languageID is provided"
    assert lot["contractTerms"]["tendererLegalForm"] == "The tenderer must be a registered company"


if __name__ == "__main__":
    pytest.main(["-v", "-s"])
