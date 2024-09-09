# tests/test_BT_769_Lot.py

import pytest
from converters.BT_769_Lot import parse_multiple_tenders, merge_multiple_tenders
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main


def test_parse_multiple_tenders():
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:TenderingTerms>
                <cbc:MultipleTendersCode listName="permission">allowed</cbc:MultipleTendersCode>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </root>
    """

    result = parse_multiple_tenders(xml_content)

    assert result is not None
    assert "tender" in result
    assert "lots" in result["tender"]
    assert len(result["tender"]["lots"]) == 1
    assert result["tender"]["lots"][0]["id"] == "LOT-0001"
    assert result["tender"]["lots"][0]["submissionTerms"]["multipleBidsAllowed"] is True


def test_merge_multiple_tenders():
    release_json = {"tender": {"lots": [{"id": "LOT-0001", "title": "Existing Lot"}]}}

    multiple_tenders_data = {
        "tender": {
            "lots": [
                {"id": "LOT-0001", "submissionTerms": {"multipleBidsAllowed": True}}
            ]
        }
    }

    merge_multiple_tenders(release_json, multiple_tenders_data)

    assert "submissionTerms" in release_json["tender"]["lots"][0]
    assert (
        release_json["tender"]["lots"][0]["submissionTerms"]["multipleBidsAllowed"]
        is True
    )


def test_bt_769_lot_multiple_tenders_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:TenderingTerms>
                <cbc:MultipleTendersCode listName="permission">allowed</cbc:MultipleTendersCode>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0002</cbc:ID>
            <cac:TenderingTerms>
                <cbc:MultipleTendersCode listName="permission">not-allowed</cbc:MultipleTendersCode>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0003</cbc:ID>
            <cac:TenderingTerms>
                <cbc:OtherCode listName="other-permission">some-value</cbc:OtherCode>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </root>
    """
    xml_file = tmp_path / "test_input_multiple_tenders.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open("output.json") as f:
        result = json.load(f)

    assert "tender" in result
    assert "lots" in result["tender"]

    lots_with_multiple_tenders = [
        lot
        for lot in result["tender"]["lots"]
        if "submissionTerms" in lot and "multipleBidsAllowed" in lot["submissionTerms"]
    ]
    assert len(lots_with_multiple_tenders) == 2

    lot_1 = next(
        (lot for lot in lots_with_multiple_tenders if lot["id"] == "LOT-0001"), None
    )
    assert lot_1 is not None
    assert lot_1["submissionTerms"]["multipleBidsAllowed"] is True

    lot_2 = next(
        (lot for lot in lots_with_multiple_tenders if lot["id"] == "LOT-0002"), None
    )
    assert lot_2 is not None
    assert lot_2["submissionTerms"]["multipleBidsAllowed"] is False

    lot_3 = next(
        (lot for lot in result["tender"]["lots"] if lot["id"] == "LOT-0003"), None
    )
    assert lot_3 is not None
    assert "submissionTerms" not in lot_3 or "multipleBidsAllowed" not in lot_3.get(
        "submissionTerms", {}
    )


if __name__ == "__main__":
    pytest.main()
