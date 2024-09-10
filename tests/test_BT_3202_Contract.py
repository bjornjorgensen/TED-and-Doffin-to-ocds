# tests/test_BT_3202_Contract.py

import pytest
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.ted_and_doffin_to_ocds.main import main


def test_bt_3202_contract_tender_id_integration(tmp_path):
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
                            <efac:SettledContract>
                                <cbc:ID schemeName="contract">CON-0001</cbc:ID>
                                <efac:LotTender>
                                    <cbc:ID schemeName="tender">TEN-0001</cbc:ID>
                                </efac:LotTender>
                            </efac:SettledContract>
                            <efac:LotTender>
                                <cbc:ID schemeName="tender">TEN-0001</cbc:ID>
                                <efac:TenderingParty>
                                    <cbc:ID schemeName="tendering-party">TPA-0001</cbc:ID>
                                </efac:TenderingParty>
                            </efac:LotTender>
                            <efac:LotResult>
                                <cbc:ID schemeName="result">RES-0001</cbc:ID>
                                <efac:SettledContract>
                                    <cbc:ID schemeName="contract">CON-0001</cbc:ID>
                                </efac:SettledContract>
                                <efac:TenderLot>
                                    <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
                                </efac:TenderLot>
                            </efac:LotResult>
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
    xml_file = tmp_path / "test_input_contract_tender_id.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open("output.json") as f:
        result = json.load(f)

    assert "parties" in result
    assert len(result["parties"]) == 1
    assert result["parties"][0]["id"] == "ORG-0001"
    assert "supplier" in result["parties"][0]["roles"]

    assert "awards" in result
    assert len(result["awards"]) == 1
    assert result["awards"][0]["id"] == "RES-0001"
    assert len(result["awards"][0]["suppliers"]) == 1
    assert result["awards"][0]["suppliers"][0]["id"] == "ORG-0001"
    assert result["awards"][0]["relatedLots"] == ["LOT-0001"]

    assert "contracts" in result
    assert len(result["contracts"]) == 1
    assert result["contracts"][0]["id"] == "CON-0001"
    assert result["contracts"][0]["relatedBids"] == ["TEN-0001"]


if __name__ == "__main__":
    pytest.main()
