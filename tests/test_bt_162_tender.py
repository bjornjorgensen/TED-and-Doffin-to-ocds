# tests/test_bt_162_Tender.py
from pathlib import Path
import pytest
import json
import sys
import logging
import tempfile

# Add the parent directory to sys.path to import main
sys.path.append(str(Path(__file__).parent.parent))
from src.ted_and_doffin_to_ocds.main import main, configure_logging


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
    output_files = list(output_dir.glob("*.json"))
    assert len(output_files) == 1, f"Expected 1 output file, got {len(output_files)}"
    with output_files[0].open() as f:
        return json.load(f)


def test_bt_162_concession_revenue_user_integration(
    tmp_path, setup_logging, temp_output_dir
):
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
                        <efac:noticeResult>
                            <efac:LotTender>
                                <cbc:ID schemeName="tender">TEN-0001</cbc:ID>
                                <efac:ConcessionRevenue>
                                    <efbc:RevenueUserAmount currencyID="EUR">350</efbc:RevenueUserAmount>
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
                        </efac:noticeResult>
                    </efext:EformsExtension>
                </ext:ExtensionContent>
            </ext:UBLExtension>
        </ext:UBLExtensions>
    </ContractAwardNotice>
    """

    # Create input XML file
    xml_file = tmp_path / "test_input_concession_revenue_user.xml"
    xml_file.write_text(xml_content)

    # Run main and get result
    result = run_main_and_get_result(xml_file, temp_output_dir)
    logger.info("Result: %s", json.dumps(result, indent=2))

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
    assert charge["id"] == "user", f"Expected charge id 'user', got {charge['id']}"
    assert charge["paidBy"] == "user", f"Expected paidBy 'user', got {charge['paidBy']}"
    assert "estimatedValue" in charge, "Expected 'estimatedValue' in charge"
    assert (
        charge["estimatedValue"]["amount"] == 350
    ), f"Expected amount 350, got {charge['estimatedValue']['amount']}"
    assert (
        charge["estimatedValue"]["currency"] == "EUR"
    ), f"Expected currency 'EUR', got {charge['estimatedValue']['currency']}"


if __name__ == "__main__":
    pytest.main(["-v", "-s"])
