import pytest
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main

def test_bt_13714_tender_integration(tmp_path):
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
                            <efac:LotTender>
                                <cbc:ID schemeName="tender">TEN-0001</cbc:ID>
                                <efac:TenderLot>
                                    <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
                                </efac:TenderLot>
                            </efac:LotTender>
                            <efac:LotTender>
                                <cbc:ID schemeName="tender">TEN-0002</cbc:ID>
                                <efac:TenderLot>
                                    <cbc:ID schemeName="Lot">LOT-0002</cbc:ID>
                                </efac:TenderLot>
                            </efac:LotTender>
                            <efac:LotTender>
                                <cbc:ID schemeName="tender">TEN-0002</cbc:ID>
                                <efac:TenderLot>
                                    <cbc:ID schemeName="Lot">LOT-0003</cbc:ID>
                                </efac:TenderLot>
                            </efac:LotTender>
                        </efac:NoticeResult>
                    </efext:EformsExtension>
                </ext:ExtensionContent>
            </ext:UBLExtension>
        </ext:UBLExtensions>
    </root>
    """
    xml_file = tmp_path / "test_input_tender_lot_identifier.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open('output.json', 'r') as f:
        result = json.load(f)

    assert "bids" in result, "Expected 'bids' in result"
    assert "details" in result["bids"], "Expected 'details' in result['bids']"
    assert len(result["bids"]["details"]) == 2, f"Expected 2 bids, got {len(result['bids']['details'])}"

    bid_1 = next(bid for bid in result["bids"]["details"] if bid["id"] == "TEN-0001")
    assert "relatedLots" in bid_1, "Expected 'relatedLots' in bid TEN-0001"
    assert bid_1["relatedLots"] == ["LOT-0001"], f"Expected ['LOT-0001'] in TEN-0001 relatedLots, got {bid_1['relatedLots']}"

    bid_2 = next(bid for bid in result["bids"]["details"] if bid["id"] == "TEN-0002")
    assert "relatedLots" in bid_2, "Expected 'relatedLots' in bid TEN-0002"
    assert set(bid_2["relatedLots"]) == set(["LOT-0002", "LOT-0003"]), f"Expected ['LOT-0002', 'LOT-0003'] in TEN-0002 relatedLots, got {bid_2['relatedLots']}"

if __name__ == "__main__":
    pytest.main()