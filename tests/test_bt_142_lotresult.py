# tests/test_bt_142_LotResult.py
from pathlib import Path
import pytest
import json
import sys

# Add the parent directory to sys.path to import main
sys.path.append(str(Path(__file__).parent.parent))
from src.ted_and_doffin_to_ocds.main import main


def test_bt_142_lotresult_integration(tmp_path):
    xml_content = """
    <root xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
          xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1">
        <ext:UBLExtensions>
            <ext:UBLExtension>
                <ext:ExtensionContent>
                    <efext:EformsExtension>
                        <efac:noticeResult>
                            <efac:LotResult>
                                <cbc:ID schemeName="result">RES-0001</cbc:ID>
                                <cbc:TenderResultCode listName="winner-selection-status">selec-w</cbc:TenderResultCode>
                                <efac:TenderLot>
                                    <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
                                </efac:TenderLot>
                            </efac:LotResult>
                            <efac:LotResult>
                                <cbc:ID schemeName="result">RES-0002</cbc:ID>
                                <cbc:TenderResultCode listName="winner-selection-status">open-nw</cbc:TenderResultCode>
                                <efac:TenderLot>
                                    <cbc:ID schemeName="Lot">LOT-0002</cbc:ID>
                                </efac:TenderLot>
                            </efac:LotResult>
                        </efac:noticeResult>
                    </efext:EformsExtension>
                </ext:ExtensionContent>
            </ext:UBLExtension>
        </ext:UBLExtensions>
    </root>
    """
    xml_file = tmp_path / "test_input_winner_chosen.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with Path("output.json").open() as f:
        result = json.load(f)

    assert "awards" in result, "Expected 'awards' in result"
    assert len(result["awards"]) == 1, f"Expected 1 award, got {len(result['awards'])}"

    award = result["awards"][0]
    assert award["id"] == "RES-0001", f"Expected award id 'RES-0001', got {award['id']}"
    assert (
        award["status"] == "active"
    ), f"Expected status 'active', got {award['status']}"
    assert (
        award["statusDetails"] == "At least one winner was chosen."
    ), "Unexpected statusDetails"
    assert award["relatedLots"] == [
        "LOT-0001",
    ], f"Expected relatedLots ['LOT-0001'], got {award['relatedLots']}"

    assert "tender" in result, "Expected 'tender' in result"
    assert "lots" in result["tender"], "Expected 'lots' in tender"
    assert (
        len(result["tender"]["lots"]) == 1
    ), f"Expected 1 lot, got {len(result['tender']['lots'])}"

    lot = result["tender"]["lots"][0]
    assert lot["id"] == "LOT-0002", f"Expected lot id 'LOT-0002', got {lot['id']}"
    assert lot["status"] == "active", f"Expected status 'active', got {lot['status']}"


if __name__ == "__main__":
    pytest.main()