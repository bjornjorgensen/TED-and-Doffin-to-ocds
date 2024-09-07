# tests/test_BT_160_Tender.py

import pytest
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main


def test_bt_160_concession_revenue_buyer_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
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
    </root>
    """
    xml_file = tmp_path / "test_input_concession_revenue_buyer.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open("output.json", "r") as f:
        result = json.load(f)

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


if __name__ == "__main__":
    pytest.main()
