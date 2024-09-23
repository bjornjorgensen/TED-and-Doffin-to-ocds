# tests/test_BT_92_Lot.py

import pytest
from ted_and_doffin_to_ocds.converters.BT_92_Lot import (
    parse_electronic_ordering,
    merge_electronic_ordering,
)
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.ted_and_doffin_to_ocds.main import main


def test_parse_electronic_ordering():
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID>LOT-0001</cbc:ID>
            <cac:TenderingTerms>
                <cac:PostAwardProcess>
                    <cbc:ElectronicOrderUsageIndicator>true</cbc:ElectronicOrderUsageIndicator>
                </cac:PostAwardProcess>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </root>
    """

    result = parse_electronic_ordering(xml_content)

    assert result is not None
    assert "tender" in result
    assert "lots" in result["tender"]
    assert len(result["tender"]["lots"]) == 1
    assert result["tender"]["lots"][0]["id"] == "LOT-0001"
    assert result["tender"]["lots"][0]["contractTerms"]["hasElectronicOrdering"] is True


def test_merge_electronic_ordering():
    release_json = {"tender": {"lots": [{"id": "LOT-0001", "title": "Existing Lot"}]}}

    electronic_ordering_data = {
        "tender": {
            "lots": [
                {"id": "LOT-0001", "contractTerms": {"hasElectronicOrdering": True}},
            ],
        },
    }

    merge_electronic_ordering(release_json, electronic_ordering_data)

    assert "contractTerms" in release_json["tender"]["lots"][0]
    assert (
        release_json["tender"]["lots"][0]["contractTerms"]["hasElectronicOrdering"]
        is True
    )


def test_bt_92_lot_electronic_ordering_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID>LOT-0001</cbc:ID>
            <cac:TenderingTerms>
                <cac:PostAwardProcess>
                    <cbc:ElectronicOrderUsageIndicator>true</cbc:ElectronicOrderUsageIndicator>
                </cac:PostAwardProcess>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
        <cac:ProcurementProjectLot>
            <cbc:ID>LOT-0002</cbc:ID>
            <cac:TenderingTerms>
                <cac:PostAwardProcess>
                    <cbc:ElectronicOrderUsageIndicator>false</cbc:ElectronicOrderUsageIndicator>
                </cac:PostAwardProcess>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </root>
    """
    xml_file = tmp_path / "test_input_electronic_ordering.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open("output.json") as f:
        result = json.load(f)

    assert "tender" in result
    assert "lots" in result["tender"]
    assert len(result["tender"]["lots"]) == 2

    lot_1 = next(
        (lot for lot in result["tender"]["lots"] if lot["id"] == "LOT-0001"),
        None,
    )
    assert lot_1 is not None
    assert lot_1["contractTerms"]["hasElectronicOrdering"] is True

    lot_2 = next(
        (lot for lot in result["tender"]["lots"] if lot["id"] == "LOT-0002"),
        None,
    )
    assert lot_2 is not None
    assert lot_2["contractTerms"]["hasElectronicOrdering"] is False


if __name__ == "__main__":
    pytest.main()
