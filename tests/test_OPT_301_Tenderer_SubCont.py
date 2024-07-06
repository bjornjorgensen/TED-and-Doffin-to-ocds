import pytest
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main

def test_opt_301_tenderer_subcont_integration(tmp_path):
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
                            </efac:LotTender>
                            <efac:TenderingParty>
                                <efac:SubContractor>
                                    <cbc:ID schemeName="organization">ORG-0012</cbc:ID>
                                </efac:SubContractor>
                            </efac:TenderingParty>
                        </efac:NoticeResult>
                        <efac:Organizations>
                            <efac:Organization>
                                <efac:Company>
                                    <cac:PartyIdentification>
                                        <cbc:ID schemeName="organization">ORG-0012</cbc:ID>
                                    </cac:PartyIdentification>
                                </efac:Company>
                            </efac:Organization>
                        </efac:Organizations>
                    </efext:EformsExtension>
                </ext:ExtensionContent>
            </ext:UBLExtension>
        </ext:UBLExtensions>
    </root>
    """
    xml_file = tmp_path / "test_input_subcontractor_id_reference.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open('output.json', 'r') as f:
        result = json.load(f)

    assert "parties" in result
    assert len(result["parties"]) == 1
    party = result["parties"][0]
    assert party["id"] == "ORG-0012"
    assert "subcontractor" in party["roles"]

    assert "bids" in result
    assert "details" in result["bids"]
    assert len(result["bids"]["details"]) == 1
    bid = result["bids"]["details"][0]
    assert bid["id"] == "TEN-0001"
    assert "lotRelatedBid" in bid
    assert bid["lotRelatedBid"] is None

    assert "subcontracting" in bid
    assert "subcontracts" in bid["subcontracting"]
    assert len(bid["subcontracting"]["subcontracts"]) == 1
    subcontract = bid["subcontracting"]["subcontracts"][0]
    assert subcontract["id"] == "1"
    assert subcontract["subcontractor"]["id"] == "ORG-0012"

if __name__ == "__main__":
    pytest.main()