# tests/test_bt_160_Tender.py
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


def test_bt_160_concession_revenue_buyer_integration(
    tmp_path, setup_logging, temp_output_dir
) -> None:
    logger = setup_logging

    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
        xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
        xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
        xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
        xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
        xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
        xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1">
        <ext:UBLExtensions>
            <ext:UBLExtension>
                <ext:ExtensionContent>
                    <efext:EformsExtension>
                        <efac:NoticeResult>
                            <efac:LotTender>
                                <cbc:ID schemeName="tender">TEN-0001</cbc:ID>
                                <efac:ConcessionRevenue>
                                    <efbc:RevenueBuyerAmount currencyID="EUR">350</efbc:RevenueBuyerAmount>
                                </efac:ConcessionRevenue>
                            </efac:LotTender>
                            <efac:SettledContract>
                                <cbc:ID schemeName="contract">CON-0001</cbc:ID>
                                <efac:LotTender>
                                    <cbc:ID schemeName="tender">TEN-0001</cbc:ID>
                                </efac:LotTender>
                            </efac:SettledContract>
                            <efac:LotResult>
                                <cbc:ID schemeName="result">RES-0001</cbc:ID>
                                <efac:SettledContract>
                                    <cbc:ID schemeName="contract">CON-0001</cbc:ID>
                                </efac:SettledContract>
                            </efac:LotResult>
                        </efac:NoticeResult>
                    </efext:EformsExtension>
                </ext:ExtensionContent>
            </ext:UBLExtension>
        </ext:UBLExtensions>
    </ContractAwardNotice>
    """

    # Create input XML file
    xml_file = tmp_path / "test_input_concession_revenue_buyer.xml"
    xml_file.write_text(xml_content)

    # Run main and get result
    result = run_main_and_get_result(xml_file, temp_output_dir)
    # logger.info("Result: %s", json.dumps(result, indent=2) # Logging disabled)

    # Verify the results
    assert "contracts" in result, "Expected 'contracts' in result"
    assert (
        len(result["contracts"]) == 1
    ), f"Expected 1 contract, got {len(result['contracts'])}"

    contract = result["contracts"][0]
    assert (
        contract["id"] == "CON-0001"
    ), f"Expected contract id 'CON-0001', got {contract['id']}"
    assert (
        contract["awardID"] == "RES-0001"
    ), f"Expected award id 'RES-0001', got {contract['awardID']}"
    assert "implementation" in contract, "Expected 'implementation' in contract"
    assert (
        "charges" in contract["implementation"]
    ), "Expected 'charges' in implementation"
    assert (
        len(contract["implementation"]["charges"]) == 1
    ), f"Expected 1 charge, got {len(contract['implementation']['charges'])}"

    charge = contract["implementation"]["charges"][0]
    assert (
        charge["id"] == "government"
    ), f"Expected charge id 'government', got {charge['id']}"
    assert (
        charge["paidBy"] == "government"
    ), f"Expected paidBy 'government', got {charge['paidBy']}"
    assert "estimatedValue" in charge, "Expected 'estimatedValue' in charge"
    assert (
        charge["estimatedValue"]["amount"] == 350
    ), f"Expected amount 350, got {charge['estimatedValue']['amount']}"
    assert (
        charge["estimatedValue"]["currency"] == "EUR"
    ), f"Expected currency 'EUR', got {charge['estimatedValue']['currency']}"


def test_bt_160_multiple_tender_contracts(
    tmp_path, setup_logging, temp_output_dir
) -> None:
    """Test with multiple tenders and contracts to ensure proper mapping."""
    
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
        xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
        xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
        xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
        xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
        xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
        xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1">
        <ext:UBLExtensions>
            <ext:UBLExtension>
                <ext:ExtensionContent>
                    <efext:EformsExtension>
                        <efac:NoticeResult>
                            <efac:LotTender>
                                <cbc:ID schemeName="tender">TEN-0001</cbc:ID>
                                <efac:ConcessionRevenue>
                                    <efbc:RevenueBuyerAmount currencyID="EUR">350</efbc:RevenueBuyerAmount>
                                </efac:ConcessionRevenue>
                            </efac:LotTender>
                            <efac:LotTender>
                                <cbc:ID schemeName="tender">TEN-0002</cbc:ID>
                                <efac:ConcessionRevenue>
                                    <efbc:RevenueBuyerAmount currencyID="USD">500</efbc:RevenueBuyerAmount>
                                </efac:ConcessionRevenue>
                            </efac:LotTender>
                            <efac:SettledContract>
                                <cbc:ID schemeName="contract">CON-0001</cbc:ID>
                                <efac:LotTender>
                                    <cbc:ID schemeName="tender">TEN-0001</cbc:ID>
                                </efac:LotTender>
                            </efac:SettledContract>
                            <efac:SettledContract>
                                <cbc:ID schemeName="contract">CON-0002</cbc:ID>
                                <efac:LotTender>
                                    <cbc:ID schemeName="tender">TEN-0002</cbc:ID>
                                </efac:LotTender>
                            </efac:SettledContract>
                            <efac:LotResult>
                                <cbc:ID schemeName="result">RES-0001</cbc:ID>
                                <efac:SettledContract>
                                    <cbc:ID schemeName="contract">CON-0001</cbc:ID>
                                </efac:SettledContract>
                            </efac:LotResult>
                            <efac:LotResult>
                                <cbc:ID schemeName="result">RES-0002</cbc:ID>
                                <efac:SettledContract>
                                    <cbc:ID schemeName="contract">CON-0002</cbc:ID>
                                </efac:SettledContract>
                            </efac:LotResult>
                        </efac:NoticeResult>
                    </efext:EformsExtension>
                </ext:ExtensionContent>
            </ext:UBLExtension>
        </ext:UBLExtensions>
    </ContractAwardNotice>
    """

    # Create input XML file
    xml_file = tmp_path / "test_input_multiple_concession_revenue.xml"
    xml_file.write_text(xml_content)

    # Run main and get result
    result = run_main_and_get_result(xml_file, temp_output_dir)

    # Verify the results
    assert "contracts" in result, "Expected 'contracts' in result"
    assert (
        len(result["contracts"]) == 2
    ), f"Expected 2 contracts, got {len(result['contracts'])}"
    
    # Sort contracts by id to ensure consistent test results
    contracts = sorted(result["contracts"], key=lambda c: c["id"])
    
    # Verify first contract
    contract1 = contracts[0]
    assert contract1["id"] == "CON-0001", f"Expected contract id 'CON-0001', got {contract1['id']}"
    assert contract1["awardID"] == "RES-0001", f"Expected award id 'RES-0001', got {contract1['awardID']}"
    charge1 = contract1["implementation"]["charges"][0]
    assert charge1["estimatedValue"]["amount"] == 350
    assert charge1["estimatedValue"]["currency"] == "EUR"
    
    # Verify second contract
    contract2 = contracts[1]
    assert contract2["id"] == "CON-0002", f"Expected contract id 'CON-0002', got {contract2['id']}"
    assert contract2["awardID"] == "RES-0002", f"Expected award id 'RES-0002', got {contract2['awardID']}"
    charge2 = contract2["implementation"]["charges"][0]
    assert charge2["estimatedValue"]["amount"] == 500
    assert charge2["estimatedValue"]["currency"] == "USD"


def test_bt_160_error_handling(
    tmp_path, setup_logging, temp_output_dir
) -> None:
    """Test error handling for malformed data."""
    
    # XML with invalid amount (non-numeric)
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
        xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
        xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
        xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
        xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
        xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
        xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1">
        <ext:UBLExtensions>
            <ext:UBLExtension>
                <ext:ExtensionContent>
                    <efext:EformsExtension>
                        <efac:NoticeResult>
                            <efac:LotTender>
                                <cbc:ID schemeName="tender">TEN-0001</cbc:ID>
                                <efac:ConcessionRevenue>
                                    <efbc:RevenueBuyerAmount currencyID="EUR">NOT-A-NUMBER</efbc:RevenueBuyerAmount>
                                </efac:ConcessionRevenue>
                            </efac:LotTender>
                            <efac:SettledContract>
                                <cbc:ID schemeName="contract">CON-0001</cbc:ID>
                                <efac:LotTender>
                                    <cbc:ID schemeName="tender">TEN-0001</cbc:ID>
                                </efac:LotTender>
                            </efac:SettledContract>
                            <efac:LotResult>
                                <cbc:ID schemeName="result">RES-0001</cbc:ID>
                                <efac:SettledContract>
                                    <cbc:ID schemeName="contract">CON-0001</cbc:ID>
                                </efac:SettledContract>
                            </efac:LotResult>
                        </efac:NoticeResult>
                    </efext:EformsExtension>
                </ext:ExtensionContent>
            </ext:UBLExtension>
        </ext:UBLExtensions>
    </ContractAwardNotice>
    """

    # Create input XML file
    xml_file = tmp_path / "test_input_error_handling.xml"
    xml_file.write_text(xml_content)

    # Run main and get result
    result = run_main_and_get_result(xml_file, temp_output_dir)

    # The function should gracefully handle the error and not include charges for the invalid amount
    for contract in result.get("contracts", []):
        if contract.get("id") == "CON-0001":
            # Either the contract should not have implementation at all, or
            # if it has implementation, it should not have government charges
            if "implementation" in contract:
                for charge in contract.get("implementation", {}).get("charges", []):
                    assert charge.get("id") != "government", "Charge with invalid amount should not be included"


if __name__ == "__main__":
    pytest.main(["-v", "-s"])
