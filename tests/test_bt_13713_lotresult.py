# tests/test_bt_13713_LotResult.py
from pathlib import Path
import pytest
import json
import sys

# Add the parent directory to sys.path to import main
sys.path.append(str(Path(__file__).parent.parent))
from src.ted_and_doffin_to_ocds.main import main


def test_bt_13713_lotresult_integration(tmp_path):
    xml_content = """
    <root xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
          xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <ext:UBLExtensions>
            <ext:UBLExtension>
                <ext:ExtensionContent>
                    <efext:EformsExtension>
                        <efac:noticeResult>
                            <efac:LotResult>
                                <cbc:ID schemeName="result">RES-0001</cbc:ID>
                                <efac:TenderLot>
                                    <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
                                </efac:TenderLot>
                            </efac:LotResult>
                            <efac:LotResult>
                                <cbc:ID schemeName="result">RES-0002</cbc:ID>
                                <efac:TenderLot>
                                    <cbc:ID schemeName="Lot">LOT-0002</cbc:ID>
                                </efac:TenderLot>
                            </efac:LotResult>
                            <efac:LotResult>
                                <cbc:ID schemeName="result">RES-0002</cbc:ID>
                                <efac:TenderLot>
                                    <cbc:ID schemeName="Lot">LOT-0003</cbc:ID>
                                </efac:TenderLot>
                            </efac:LotResult>
                        </efac:noticeResult>
                    </efext:EformsExtension>
                </ext:ExtensionContent>
            </ext:UBLExtension>
        </ext:UBLExtensions>
    </root>
    """
    xml_file = tmp_path / "test_input_result_lot_identifier.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with Path("output.json").open() as f:
        result = json.load(f)

    assert "awards" in result, "Expected 'awards' in result"
    assert len(result["awards"]) == 2, f"Expected 2 awards, got {len(result['awards'])}"

    award_1 = next(award for award in result["awards"] if award["id"] == "RES-0001")
    assert "relatedLots" in award_1, "Expected 'relatedLots' in award RES-0001"
    assert award_1["relatedLots"] == [
        "LOT-0001",
    ], f"Expected ['LOT-0001'] in RES-0001 relatedLots, got {award_1['relatedLots']}"

    award_2 = next(award for award in result["awards"] if award["id"] == "RES-0002")
    assert "relatedLots" in award_2, "Expected 'relatedLots' in award RES-0002"
    assert (
        set(award_2["relatedLots"]) == {"LOT-0002", "LOT-0003"}
    ), f"Expected ['LOT-0002', 'LOT-0003'] in RES-0002 relatedLots, got {award_2['relatedLots']}"


if __name__ == "__main__":
    pytest.main()
