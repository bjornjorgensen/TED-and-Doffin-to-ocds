# tests/test_OPT_301_Tenderer_MainCont.py

import pytest
import sys
from pathlib import Path

# Add the parent directory to sys.path to import main
sys.path.append(str(Path(__file__).parent.parent))
from src.ted_and_doffin_to_ocds.main import main


def test_opt_301_tenderer_maincont_integration(tmp_path):
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
                        <efac:noticeResult>
                            <efac:LotTender>
                                <cbc:ID schemeName="tender">TEN-0001</cbc:ID>
                                <cbc:RankCode>1</cbc:RankCode>
                                <efac:TenderLot>
                                    <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
                                </efac:TenderLot>
                            </efac:LotTender>
                            <efac:Tenderingparty>
                                <efac:SubContractor>
                                    <cbc:ID schemeName="organization">ORG-0012</cbc:ID>
                                    <efac:MainContractor>
                                        <cbc:ID schemeName="organization">ORG-0005</cbc:ID>
                                    </efac:MainContractor>
                                </efac:SubContractor>
                            </efac:Tenderingparty>
                        </efac:noticeResult>
                        <efac:organizations>
                            <efac:organization>
                                <efac:company>
                                    <cac:partyIdentification>
                                        <cbc:ID schemeName="organization">ORG-0005</cbc:ID>
                                    </cac:partyIdentification>
                                    <cac:partyName>
                                        <cbc:Name>Tendering company Ltd</cbc:Name>
                                    </cac:partyName>
                                </efac:company>
                            </efac:organization>
                        </efac:organizations>
                    </efext:EformsExtension>
                </ext:ExtensionContent>
            </ext:UBLExtension>
        </ext:UBLExtensions>
    </root>
    """
    xml_file = tmp_path / "test_input_tenderer_maincont.xml"
    xml_file.write_text(xml_content)

    result = main(str(xml_file), "ocds-test-prefix")

    assert result is not None
    assert "parties" in result
    assert len(result["parties"]) == 1
    party = result["parties"][0]
    assert party["id"] == "ORG-0005"
    assert "roles" in party
    assert "tenderer" in party["roles"]

    assert "bids" in result
    assert "details" in result["bids"]
    assert len(result["bids"]["details"]) == 1
    bid = result["bids"]["details"][0]
    assert bid["id"] == "TEN-0001"
    assert bid["rank"] == 1
    assert bid["relatedLots"] == ["LOT-0001"]
    assert "subcontracting" in bid
    assert "subcontracts" in bid["subcontracting"]
    assert len(bid["subcontracting"]["subcontracts"]) == 1
    subcontract = bid["subcontracting"]["subcontracts"][0]
    assert subcontract["id"] == "1"
    assert subcontract["subcontractor"]["id"] == "ORG-0012"
    assert len(subcontract["mainContractors"]) == 1
    main_contractor = subcontract["mainContractors"][0]
    assert main_contractor["id"] == "ORG-0005"
    assert main_contractor["name"] == "Tendering company Ltd"


if __name__ == "__main__":
    pytest.main()
