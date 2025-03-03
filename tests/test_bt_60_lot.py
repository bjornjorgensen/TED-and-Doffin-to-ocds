# tests/test_bt_60_Lot.py
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


def test_bt_60_lot_integration(tmp_path, setup_logging, temp_output_dir) -> None:
    logger = setup_logging

    # Updated XML to use the correct xpath for BT-60
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
        xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
        xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
        xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1">
        <cbc:ID>notice-1</cbc:ID>
        <cbc:ContractFolderID>cf-1</cbc:ContractFolderID>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">lot-1</cbc:ID>
            <cac:TenderingTerms>
                <cbc:FundingProgramCode listName="eu-funded">eu-funds</cbc:FundingProgramCode>
                <cbc:FundingProgram>European Regional Development Fund</cbc:FundingProgram>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
        <efac:Funding>
            <cbc:FundingProgramCode listName="eu-funded">eu-funds</cbc:FundingProgramCode>
            <cbc:FundingProjectIdentifier>ERDF-2023-XYZ</cbc:FundingProjectIdentifier>
        </efac:Funding>
    </ContractAwardNotice>
    """

    # Create input XML file
    xml_file = tmp_path / "test_input_eu_funds.xml"
    xml_file.write_text(xml_content)

    # Run main and get result
    result = run_main_and_get_result(xml_file, temp_output_dir)

    # Verify the results
    assert "parties" in result, "Expected 'parties' in result"
    assert len(result["parties"]) == 1, f"Expected 1 party, got {len(result['parties'])}"

    eu_party = result["parties"][0]
    assert eu_party["name"] == "European Union", f"Expected party name 'European Union', got {eu_party['name']}"
    assert "funder" in eu_party["roles"], "Expected 'funder' in party roles"
    assert eu_party["id"], "Expected EU party to have an ID"
    
    # Check for finance object in planning.budget.finance
    assert "planning" in result, "Expected 'planning' in result"
    assert "budget" in result["planning"], "Expected 'budget' in planning"
    assert "finance" in result["planning"]["budget"], "Expected 'finance' in budget"
    assert len(result["planning"]["budget"]["finance"]) > 0, "Expected at least one finance object"
    
    finance_obj = result["planning"]["budget"]["finance"][0]
    assert "id" in finance_obj, "Expected 'id' in finance object"
    assert "description" in finance_obj, "Expected 'description' in finance object"
    if "FundingProjectIdentifier" in xml_content:
        assert finance_obj["description"] == "ERDF-2023-XYZ", "Expected description to match FundingProjectIdentifier"
    assert "financingParty" in finance_obj, "Expected 'financingParty' in finance object"
    assert "name" in finance_obj["financingParty"], "Expected 'name' in financingParty"
    assert finance_obj["financingParty"]["name"] == "European Union", "Expected financingParty name to be 'European Union'"
    assert "id" in finance_obj["financingParty"], "Expected 'id' in financingParty"
    assert finance_obj["financingParty"]["id"] == eu_party["id"], "Expected financingParty id to match EU party id"
    assert "relatedLots" in finance_obj, "Expected 'relatedLots' in finance object"
    assert "lot-1" in finance_obj["relatedLots"], "Expected lot-1 in relatedLots"


def test_bt_60_multiple_lots(tmp_path, setup_logging, temp_output_dir) -> None:
    logger = setup_logging

    # Updated XML to use the correct xpath for BT-60
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
        xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
        xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
        xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1">
        <cbc:ID>notice-1</cbc:ID>
        <cbc:ContractFolderID>cf-1</cbc:ContractFolderID>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">lot-1</cbc:ID>
            <cac:TenderingTerms>
                <cbc:FundingProgramCode listName="eu-funded">eu-funds</cbc:FundingProgramCode>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">lot-2</cbc:ID>
            <cac:TenderingTerms>
                <cbc:FundingProgramCode listName="eu-funded">eu-funds</cbc:FundingProgramCode>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
        <efac:Funding>
            <cbc:FundingProgramCode listName="eu-funded">eu-funds</cbc:FundingProgramCode>
        </efac:Funding>
    </ContractAwardNotice>
    """

    # Create input XML file
    xml_file = tmp_path / "test_input_eu_funds_multiple_lots.xml"
    xml_file.write_text(xml_content)

    # Run main and get result
    result = run_main_and_get_result(xml_file, temp_output_dir)

    # Verify the results
    assert "parties" in result, "Expected 'parties' in result"
    eu_party = None
    for party in result["parties"]:
        if party["name"] == "European Union" and "funder" in party["roles"]:
            eu_party = party
            break
    
    assert eu_party is not None, "Expected European Union party with funder role"
    
    # Check for finance object in planning.budget.finance
    assert "planning" in result, "Expected 'planning' in result"
    assert "budget" in result["planning"], "Expected 'budget' in planning"
    assert "finance" in result["planning"]["budget"], "Expected 'finance' in budget"
    
    # Find the EU finance object
    eu_finance = None
    for finance in result["planning"]["budget"]["finance"]:
        if finance.get("financingParty", {}).get("name") == "European Union":
            eu_finance = finance
            break
    
    assert eu_finance is not None, "Expected EU finance object"
    assert "relatedLots" in eu_finance, "Expected 'relatedLots' in EU finance object"
    assert "lot-1" in eu_finance["relatedLots"], "Expected lot-1 in relatedLots"
    assert "lot-2" in eu_finance["relatedLots"], "Expected lot-2 in relatedLots"


def test_bt_60_no_eu_funds(tmp_path, setup_logging, temp_output_dir) -> None:
    logger = setup_logging

    # Updated XML to use the correct xpath for BT-60
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
        xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
        xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cbc:ID>notice-1</cbc:ID>
        <cbc:ContractFolderID>cf-1</cbc:ContractFolderID>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">lot-1</cbc:ID>
            <cac:TenderingTerms>
                <!-- No EU funding info -->
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </ContractAwardNotice>
    """

    # Create input XML file
    xml_file = tmp_path / "test_input_no_eu_funds.xml"
    xml_file.write_text(xml_content)

    # Run main and get result
    result = run_main_and_get_result(xml_file, temp_output_dir)

    # Verify the results - no EU party should exist
    eu_party = None
    if "parties" in result:
        for party in result["parties"]:
            if party.get("name") == "European Union" and "funder" in party.get("roles", []):
                eu_party = party
                break
    
    assert eu_party is None, "Expected no European Union party with funder role"
    
    # Check that there's no EU funds finance object
    eu_finance = None
    if "planning" in result and "budget" in result.get("planning", {}) and "finance" in result.get("planning", {}).get("budget", {}):
        for finance in result["planning"]["budget"]["finance"]:
            if finance.get("financingParty", {}).get("name") == "European Union":
                eu_finance = finance
                break
    
    assert eu_finance is None, "Expected no EU finance object"


if __name__ == "__main__":
    pytest.main(["-v"])
