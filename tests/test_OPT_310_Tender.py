# tests/test_OPT_310_Tender.py

import pytest
import json
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main

def test_opt_310_tender_integration(tmp_path):
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
                                <efac:TenderingParty>
                                    <cbc:ID schemeName="tendering-party">TPA-0001</cbc:ID>
                                </efac:TenderingParty>
                                <efac:TenderLot>
                                    <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
                                </efac:TenderLot>
                            </efac:LotTender>
                            <efac:TenderingParty>
                                <cbc:ID schemeName="tendering-party">TPA-0001</cbc:ID>
                                <efac:Tenderer>
                                    <cbc:ID schemeName="organization">ORG-0001</cbc:ID>
                                </efac:Tenderer>
                            </efac:TenderingParty>
                        </efac:NoticeResult>
                    </efext:EformsExtension>
                </ext:ExtensionContent>
            </ext:UBLExtension>
        </ext:UBLExtensions>
    </root>
    """
    xml_file = tmp_path / "test_input_tendering_party_id_reference.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open('output.json', 'r') as f:
        result = json.load(f)

    assert "parties" in result
    assert len(result["parties"]) == 1
    party = result["parties"][0]
    assert party["id"] == "ORG-0001"
    assert "roles" in party
    assert "tenderer" in party["roles"]

    assert "bids" in result
    assert "details" in result["bids"]
    assert len(result["bids"]["details"]) == 1
    bid = result["bids"]["details"][0]
    assert bid["id"] == "TEN-0001"
    assert "tenderers" in bid
    assert len(bid["tenderers"]) == 1
    assert bid["tenderers"][0]["id"] == "ORG-0001"

if __name__ == "__main__":
    pytest.main()