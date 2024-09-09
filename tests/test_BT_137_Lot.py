# tests/test_BT_137_Lot.py

import pytest
from converters.BT_137_Lot import (
    parse_purpose_lot_identifier,
    merge_purpose_lot_identifier,
)
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main


def test_parse_purpose_lot_identifier():
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
        </cac:ProcurementProjectLot>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0002</cbc:ID>
        </cac:ProcurementProjectLot>
    </root>
    """

    result = parse_purpose_lot_identifier(xml_content)

    assert result is not None
    assert "tender" in result
    assert "lots" in result["tender"]
    assert len(result["tender"]["lots"]) == 2
    assert result["tender"]["lots"][0]["id"] == "LOT-0001"
    assert result["tender"]["lots"][1]["id"] == "LOT-0002"


def test_merge_purpose_lot_identifier():
    release_json = {"tender": {"lots": [{"id": "LOT-0001", "title": "Existing Lot"}]}}

    purpose_lot_identifier_data = {
        "tender": {"lots": [{"id": "LOT-0001"}, {"id": "LOT-0002"}]}
    }

    merge_purpose_lot_identifier(release_json, purpose_lot_identifier_data)

    assert len(release_json["tender"]["lots"]) == 2
    assert release_json["tender"]["lots"][0]["id"] == "LOT-0001"
    assert release_json["tender"]["lots"][0]["title"] == "Existing Lot"
    assert release_json["tender"]["lots"][1]["id"] == "LOT-0002"


def test_bt_137_lot_purpose_lot_identifier_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
        </cac:ProcurementProjectLot>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0002</cbc:ID>
        </cac:ProcurementProjectLot>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0003</cbc:ID>
        </cac:ProcurementProjectLot>
    </root>
    """
    xml_file = tmp_path / "test_input_purpose_lot_identifier.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open("output.json") as f:
        result = json.load(f)

    assert "tender" in result
    assert "lots" in result["tender"]
    assert len(result["tender"]["lots"]) == 3

    lot_ids = [lot["id"] for lot in result["tender"]["lots"]]
    assert "LOT-0001" in lot_ids
    assert "LOT-0002" in lot_ids
    assert "LOT-0003" in lot_ids


if __name__ == "__main__":
    pytest.main()
