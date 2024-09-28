# tests/test_bt_60_Lot.py
from pathlib import Path
import pytest
import json
import sys

# Add the parent directory to sys.path to import main
sys.path.append(str(Path(__file__).parent.parent))
from src.ted_and_doffin_to_ocds.main import main


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

    with Path("output.json").open() as f:
        result = json.load(f)

    assert "parties" in result, "Expected 'parties' in result"
    assert (
        len(result["parties"]) == 1
    ), f"Expected 1 party, got {len(result['parties'])}"

    eu_party = result["parties"][0]
    assert (
        eu_party["name"] == "European Union"
    ), f"Expected party name 'European Union', got {eu_party['name']}"
    assert "funder" in eu_party["roles"], "Expected 'funder' in party roles"


if __name__ == "__main__":
    pytest.main()
