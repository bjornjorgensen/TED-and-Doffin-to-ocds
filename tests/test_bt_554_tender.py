# tests/test_bt_554_Tender.py
from pathlib import Path
import pytest
import json
import sys

# Add the parent directory to sys.path to import main
sys.path.append(str(Path(__file__).parent.parent))
from src.ted_and_doffin_to_ocds.main import main


def test_bt_554_tender_integration(tmp_path):
    xml_content = """
    <root xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
          xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1">
        <efac:noticeResult>
            <efac:LotTender>
                <cbc:ID schemeName="tender">TEN-0001</cbc:ID>
                <efac:SubcontractingTerm>
                    <efbc:TermCode listName="applicability">applicable</efbc:TermCode>
                    <efbc:TermDescription languageID="ENG">The subcontracting will be...</efbc:TermDescription>
                </efac:SubcontractingTerm>
                <efac:TenderLot>
                    <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
                </efac:TenderLot>
            </efac:LotTender>
        </efac:noticeResult>
    </root>
    """
    xml_file = tmp_path / "test_input_subcontracting_description.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with Path("output.json").open() as f:
        result = json.load(f)

    assert "bids" in result, "Expected 'bids' in result"
    assert "details" in result["bids"], "Expected 'details' in bids"
    assert (
        len(result["bids"]["details"]) == 1
    ), f"Expected 1 bid, got {len(result['bids']['details'])}"

    bid = result["bids"]["details"][0]
    assert bid["id"] == "TEN-0001", f"Expected bid id 'TEN-0001', got {bid['id']}"
    assert "subcontracting" in bid, "Expected 'subcontracting' in bid"
    assert (
        "description" in bid["subcontracting"]
    ), "Expected 'description' in bid subcontracting"
    assert (
        bid["subcontracting"]["description"] == "The subcontracting will be..."
    ), f"Expected description 'The subcontracting will be...', got {bid['subcontracting']['description']}"
    assert bid["relatedLots"] == [
        "LOT-0001",
    ], f"Expected relatedLots ['LOT-0001'], got {bid['relatedLots']}"


if __name__ == "__main__":
    pytest.main()