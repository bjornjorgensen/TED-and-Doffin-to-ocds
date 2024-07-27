# tests/test_BT_710_LotResult.py

import pytest
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main

def test_bt_710_lot_result_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
          xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1">
        <ext:UBLExtensions>
            <ext:UBLExtension>
                <ext:ExtensionContent>
                    <efext:EformsExtension>
                        <efac:NoticeResult>
                            <efac:LotResult>
                                <cbc:LowerTenderAmount currencyID="EUR">1230000</cbc:LowerTenderAmount>
                                <efac:TenderLot>
                                    <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
                                </efac:TenderLot>
                            </efac:LotResult>
                        </efac:NoticeResult>
                    </efext:EformsExtension>
                </ext:ExtensionContent>
            </ext:UBLExtension>
        </ext:UBLExtensions>
    </root>
    """
    xml_file = tmp_path / "test_input_tender_value_lowest.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open('output.json', 'r') as f:
        result = json.load(f)

    assert "bids" in result, "Expected 'bids' in result"
    assert "statistics" in result["bids"], "Expected 'statistics' in bids"
    assert len(result["bids"]["statistics"]) == 1, f"Expected 1 statistic, got {len(result['bids']['statistics'])}"

    statistic = result["bids"]["statistics"][0]
    assert statistic["measure"] == "lowestValidBidValue", f"Expected measure 'lowestValidBidValue', got {statistic['measure']}"
    assert statistic["value"] == 1230000, f"Expected value 1230000, got {statistic['value']}"
    assert statistic["currency"] == "EUR", f"Expected currency 'EUR', got {statistic['currency']}"
    assert statistic["relatedLot"] == "LOT-0001", f"Expected relatedLot 'LOT-0001', got {statistic['relatedLot']}"

if __name__ == "__main__":
    pytest.main()