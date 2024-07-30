# tests/test_BT_773_Tender.py

import pytest
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main

def test_bt_773_tender_subcontracting_integration(tmp_path):
    xml_content = """
    <root xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
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
                                <efac:SubcontractingTerm>
                                    <efbc:TermCode listName="applicability">yes</efbc:TermCode>
                                </efac:SubcontractingTerm>
                            </efac:LotTender>
                            <efac:LotTender>
                                <cbc:ID schemeName="tender">TEN-0002</cbc:ID>
                                <efac:SubcontractingTerm>
                                    <efbc:TermCode listName="applicability">no</efbc:TermCode>
                                </efac:SubcontractingTerm>
                            </efac:LotTender>
                            <efac:LotTender>
                                <cbc:ID schemeName="tender">TEN-0003</cbc:ID>
                            </efac:LotTender>
                        </efac:NoticeResult>
                    </efext:EformsExtension>
                </ext:ExtensionContent>
            </ext:UBLExtension>
        </ext:UBLExtensions>
    </root>
    """
    xml_file = tmp_path / "test_input_subcontracting.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open('output.json', 'r') as f:
        result = json.load(f)

    assert "bids" in result
    assert "details" in result["bids"]
    
    bids = result["bids"]["details"]
    assert len(bids) == 2  # Only bids with subcontracting information should be included

    bid_1 = next((bid for bid in bids if bid["id"] == "TEN-0001"), None)
    assert bid_1 is not None
    assert bid_1["hasSubcontracting"] is True

    bid_2 = next((bid for bid in bids if bid["id"] == "TEN-0002"), None)
    assert bid_2 is not None
    assert bid_2["hasSubcontracting"] is False

    bid_3 = next((bid for bid in bids if bid["id"] == "TEN-0003"), None)
    assert bid_3 is None  # This bid should not be included as it has no subcontracting information

if __name__ == "__main__":
    pytest.main()