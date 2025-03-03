import json
import sys
import tempfile
from pathlib import Path

import pytest

# Add the parent directory to sys.path to import main
sys.path.append(str(Path(__file__).parent.parent))
from src.ted_and_doffin_to_ocds.main import main


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


def test_bt_5011_contract_integration(tmp_path, temp_output_dir) -> None:
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
                            <efac:SettledContract>
                                <cbc:ID schemeName="contract">CON-0001</cbc:ID>
                                <efac:Funding>
                                    <efbc:FinancingIdentifier>2021/1234</efbc:FinancingIdentifier>
                                </efac:Funding>
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

    xml_file = tmp_path / "test_input_contract_eu_funds_financing_identifier.xml"
    xml_file.write_text(xml_content)

    result = run_main_and_get_result(xml_file, temp_output_dir)

    # Check if parties are properly created
    assert "parties" in result, "Expected 'parties' in result"
    eu_party = next(
        (party for party in result["parties"] if party["name"] == "European Union"),
        None,
    )
    assert eu_party is not None, "Expected to find European Union party"
    assert "roles" in eu_party, "Expected 'roles' in European Union party"
    assert (
        "funder" in eu_party["roles"]
    ), "Expected 'funder' role in European Union party roles"
    assert "id" in eu_party, "Expected European Union party to have an ID"

    # Check if contract and financing data is properly created
    assert "contracts" in result, "Expected 'contracts' in result"
    contract = next(
        (contract for contract in result["contracts"] if contract["id"] == "CON-0001"),
        None,
    )
    assert contract is not None, "Expected to find contract CON-0001"
    assert "finance" in contract, "Expected 'finance' in contract"

    finance = contract["finance"]
    assert len(finance) == 1, f"Expected 1 finance item, got {len(finance)}"
    assert (
        finance[0]["id"] == "2021/1234"
    ), f"Expected finance id '2021/1234', got {finance[0]['id']}"
    
    # Check using camelCase key (correct property name)
    assert "financingParty" in finance[0], "Expected 'financingParty' in finance item"
    assert (
        finance[0]["financingParty"]["name"] == "European Union"
    ), "Expected financingParty name to be 'European Union'"
    assert (
        finance[0]["financingParty"]["id"] == eu_party["id"]
    ), "Expected financingParty id to match European Union party id"


def test_bt_5011_contract_with_multiple_financing_ids(tmp_path, temp_output_dir) -> None:
    """Test with multiple financing identifiers in the same contract."""
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
                            <efac:SettledContract>
                                <cbc:ID schemeName="contract">CON-0001</cbc:ID>
                                <efac:Funding>
                                    <efbc:FinancingIdentifier>2021/1234</efbc:FinancingIdentifier>
                                </efac:Funding>
                                <efac:Funding>
                                    <efbc:FinancingIdentifier>2021/5678</efbc:FinancingIdentifier>
                                </efac:Funding>
                            </efac:SettledContract>
                        </efac:NoticeResult>
                    </efext:EformsExtension>
                </ext:ExtensionContent>
            </ext:UBLExtension>
        </ext:UBLExtensions>
    </ContractAwardNotice>
    """

    xml_file = tmp_path / "test_input_multiple_financing_ids.xml"
    xml_file.write_text(xml_content)

    result = run_main_and_get_result(xml_file, temp_output_dir)

    # Verify EU party exists
    assert "parties" in result
    eu_party = next(
        (party for party in result["parties"] if party["name"] == "European Union"),
        None,
    )
    assert eu_party is not None

    # Verify contract exists with multiple finance items
    assert "contracts" in result
    contract = next(
        (contract for contract in result["contracts"] if contract["id"] == "CON-0001"),
        None,
    )
    assert contract is not None
    assert "finance" in contract
    
    finance = contract["finance"]
    assert len(finance) == 2, "Expected 2 finance items for multiple funding identifiers"
    
    # Check that both financing identifiers are present
    finance_ids = [item["id"] for item in finance]
    assert "2021/1234" in finance_ids
    assert "2021/5678" in finance_ids
    
    # Check that all finance items refer to the EU party
    for item in finance:
        assert item["financingParty"]["id"] == eu_party["id"]
        assert item["financingParty"]["name"] == "European Union"


if __name__ == "__main__":
    pytest.main(["-v", "-s"])
