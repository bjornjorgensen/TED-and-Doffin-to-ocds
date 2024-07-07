# tests/test_BT_60_Lot.py

import pytest
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main

def test_bt_60_lot_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1">
        <efac:Funding>
            <cbc:FundingProgramCode listName="eu-funded">eu-funds</cbc:FundingProgramCode>
        </efac:Funding>
    </root>
    """
    xml_file = tmp_path / "test_input_eu_funds.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open('output.json', 'r') as f:
        result = json.load(f)

    assert "parties" in result, "Expected 'parties' in result"
    eu_party = next((party for party in result["parties"] if party["name"] == "European Union"), None)
    assert eu_party is not None, "Expected to find European Union party"
    assert eu_party["id"] == "1", f"Expected party id '1', got {eu_party['id']}"
    assert "roles" in eu_party, "Expected 'roles' in European Union party"
    assert "funder" in eu_party["roles"], "Expected 'funder' role in European Union party roles"

if __name__ == "__main__":
    pytest.main()