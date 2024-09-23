# tests/test_bt_5010_Lot.py

import pytest
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.ted_and_doffin_to_ocds.main import main


def test_bt_5010_lot_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
          xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
          xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:TenderingTerms>
                <ext:UBLExtensions>
                    <ext:UBLExtension>
                        <ext:ExtensionContent>
                            <efext:EformsExtension>
                                <efac:Funding>
                                    <efbc:FinancingIdentifier>CON_PRO-123/ABC</efbc:FinancingIdentifier>
                                </efac:Funding>
                            </efext:EformsExtension>
                        </ext:ExtensionContent>
                    </ext:UBLExtension>
                </ext:UBLExtensions>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </root>
    """
    xml_file = tmp_path / "test_input_eu_funds_financing_identifier.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open("output.json") as f:
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

    assert "planning" in result, "Expected 'planning' in result"
    assert "budget" in result["planning"], "Expected 'budget' in planning"
    assert "finance" in result["planning"]["budget"], "Expected 'finance' in budget"

    finance = result["planning"]["budget"]["finance"]
    assert len(finance) == 1, f"Expected 1 finance item, got {len(finance)}"
    assert (
        finance[0]["id"] == "CON_PRO-123/ABC"
    ), f"Expected finance id 'CON_PRO-123/ABC', got {finance[0]['id']}"
    assert (
        finance[0]["financingparty"]["name"] == "European Union"
    ), "Expected financingparty name to be 'European Union'"
    assert (
        finance[0]["financingparty"]["id"] == eu_party["id"]
    ), "Expected financingparty id to match European Union party id"
    assert finance[0]["relatedLots"] == [
        "LOT-0001",
    ], "Expected relatedLots to contain 'LOT-0001'"


if __name__ == "__main__":
    pytest.main()
