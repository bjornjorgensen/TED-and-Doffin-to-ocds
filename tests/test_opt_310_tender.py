# tests/test_OPT_310_Tender.py

import pytest
import json
import sys
from pathlib import Path

# Add the parent directory to sys.path to import main
sys.path.append(str(Path(__file__).parent.parent))
from src.ted_and_doffin_to_ocds.main import main


def test_opt_310_tendering_party_id_reference_integration(tmp_path):
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
                                <efac:Tenderingparty>
                                    <cbc:ID schemeName="tendering-party">TPA-0001</cbc:ID>
                                </efac:Tenderingparty>
                                <efac:TenderLot>
                                    <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
                                </efac:TenderLot>
                            </efac:LotTender>
                            <efac:Tenderingparty>
                                <cbc:ID schemeName="tendering-party">TPA-0001</cbc:ID>
                                <efac:Tenderer>
                                    <cbc:ID schemeName="organization">ORG-0011</cbc:ID>
                                </efac:Tenderer>
                            </efac:Tenderingparty>
                        </efac:noticeResult>
                    </efext:EformsExtension>
                </ext:ExtensionContent>
            </ext:UBLExtension>
        </ext:UBLExtensions>
    </root>
    """
    xml_file = tmp_path / "test_input_tendering_party_id_reference.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with Path("output.json").open() as f:
        result = json.load(f)

    assert "parties" in result, "Expected 'parties' in result"
    assert (
        len(result["parties"]) == 1
    ), f"Expected 1 party, got {len(result['parties'])}"
    assert (
        result["parties"][0]["id"] == "ORG-0011"
    ), f"Expected party id 'ORG-0011', got {result['parties'][0]['id']}"
    assert "roles" in result["parties"][0], "Expected 'roles' in party"
    assert (
        "tenderer" in result["parties"][0]["roles"]
    ), "Expected 'tenderer' role in party"

    assert "bids" in result, "Expected 'bids' in result"
    assert "details" in result["bids"], "Expected 'details' in bids"
    assert (
        len(result["bids"]["details"]) == 1
    ), f"Expected 1 bid, got {len(result['bids']['details'])}"

    bid = result["bids"]["details"][0]
    assert bid["id"] == "TEN-0001", f"Expected bid id 'TEN-0001', got {bid['id']}"
    assert "tenderers" in bid, "Expected 'tenderers' in bid"
    assert (
        len(bid["tenderers"]) == 1
    ), f"Expected 1 tenderer, got {len(bid['tenderers'])}"
    assert (
        bid["tenderers"][0]["id"] == "ORG-0011"
    ), f"Expected tenderer id 'ORG-0011', got {bid['tenderers'][0]['id']}"


if __name__ == "__main__":
    pytest.main()