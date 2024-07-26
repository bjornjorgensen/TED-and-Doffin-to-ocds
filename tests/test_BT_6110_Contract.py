# tests/test_BT_6110_Contract.py

import pytest
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main

def test_bt_6110_contract_integration(tmp_path):
    xml_content = """
    <root xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1">
        <efac:NoticeResult>
            <efac:SettledContract>
                <cbc:ID schemeName="contract">CON-0001</cbc:ID>
                <efac:Funding>
                    <cbc:Description>Program for the development ...</cbc:Description>
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
    xml_file = tmp_path / "test_input_contract_eu_funds_details.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open('output.json', 'r') as f:
        result = json.load(f)

    assert "contracts" in result, "Expected 'contracts' in result"
    assert len(result["contracts"]) == 1, f"Expected 1 contract, got {len(result['contracts'])}"

    contract = result["contracts"][0]
    assert contract["id"] == "CON-0001", f"Expected contract id 'CON-0001', got {contract['id']}"
    assert "finance" in contract, "Expected 'finance' in contract"
    assert len(contract["finance"]) == 1, f"Expected 1 finance entry, got {len(contract['finance'])}"
    assert contract["finance"][0]["description"] == "Program for the development ...", f"Expected description 'Program for the development ...', got {contract['finance'][0]['description']}"
    assert contract["awardID"] == "RES-0001", f"Expected awardID 'RES-0001', got {contract.get('awardID')}"

if __name__ == "__main__":
    pytest.main()