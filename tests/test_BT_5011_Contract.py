# tests/test_BT_5011_Contract.py

import pytest
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main


def test_bt_5011_contract_integration(tmp_path):
    xml_content = """
    <root xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
          xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
          xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1">
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
    </root>
    """
    xml_file = tmp_path / "test_input_contract_eu_funds_financing_identifier.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open("output.json", "r") as f:
        result = json.load(f)

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
    assert (
        finance[0]["financingParty"]["name"] == "European Union"
    ), "Expected financingParty name to be 'European Union'"
    assert (
        finance[0]["financingParty"]["id"] == eu_party["id"]
    ), "Expected financingParty id to match European Union party id"


if __name__ == "__main__":
    pytest.main()
