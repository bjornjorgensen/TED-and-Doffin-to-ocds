# tests/test_BT_78_Lot.py

import pytest
from ted_and_doffin_to_ocds.converters.BT_78_Lot import (
    parse_security_clearance_deadline,
    merge_security_clearance_deadline,
)
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.ted_and_doffin_to_ocds.main import main


def test_parse_security_clearance_deadline():
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:TenderingTerms>
                <cbc:LatestSecurityClearanceDate>2019-11-15+01:00</cbc:LatestSecurityClearanceDate>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </root>
    """

    result = parse_security_clearance_deadline(xml_content)

    assert result is not None
    assert "tender" in result
    assert "lots" in result["tender"]
    assert len(result["tender"]["lots"]) == 1
    assert result["tender"]["lots"][0]["id"] == "LOT-0001"
    assert "milestones" in result["tender"]["lots"][0]
    assert len(result["tender"]["lots"][0]["milestones"]) == 1
    assert result["tender"]["lots"][0]["milestones"][0]["id"] == "1"
    assert (
        result["tender"]["lots"][0]["milestones"][0]["type"]
        == "securityClearanceDeadline"
    )
    assert (
        result["tender"]["lots"][0]["milestones"][0]["dueDate"]
        == "2019-11-15T23:59:59+01:00"
    )


def test_merge_security_clearance_deadline():
    release_json = {"tender": {"lots": [{"id": "LOT-0001", "title": "Existing Lot"}]}}

    security_clearance_data = {
        "tender": {
            "lots": [
                {
                    "id": "LOT-0001",
                    "milestones": [
                        {
                            "id": "1",
                            "type": "securityClearanceDeadline",
                            "dueDate": "2019-11-15T23:59:59+01:00",
                        },
                    ],
                },
            ],
        },
    }

    merge_security_clearance_deadline(release_json, security_clearance_data)

    assert "milestones" in release_json["tender"]["lots"][0]
    assert len(release_json["tender"]["lots"][0]["milestones"]) == 1
    assert (
        release_json["tender"]["lots"][0]["milestones"][0]["type"]
        == "securityClearanceDeadline"
    )
    assert (
        release_json["tender"]["lots"][0]["milestones"][0]["dueDate"]
        == "2019-11-15T23:59:59+01:00"
    )


def test_bt_78_lot_security_clearance_deadline_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:TenderingTerms>
                <cbc:LatestSecurityClearanceDate>2019-11-15+01:00</cbc:LatestSecurityClearanceDate>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0002</cbc:ID>
            <cac:TenderingTerms>
                <cbc:LatestSecurityClearanceDate>2019-12-01Z</cbc:LatestSecurityClearanceDate>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0003</cbc:ID>
            <cac:TenderingTerms>
                <cbc:OtherTerms>No security clearance needed</cbc:OtherTerms>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </root>
    """
    xml_file = tmp_path / "test_input_security_clearance_deadline.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open("output.json") as f:
        result = json.load(f)

    assert "tender" in result
    assert "lots" in result["tender"]

    lots_with_milestones = [
        lot for lot in result["tender"]["lots"] if "milestones" in lot
    ]
    assert len(lots_with_milestones) == 2

    lot_1 = next((lot for lot in lots_with_milestones if lot["id"] == "LOT-0001"), None)
    assert lot_1 is not None
    assert lot_1["milestones"][0]["type"] == "securityClearanceDeadline"
    assert lot_1["milestones"][0]["dueDate"] == "2019-11-15T23:59:59+01:00"

    lot_2 = next((lot for lot in lots_with_milestones if lot["id"] == "LOT-0002"), None)
    assert lot_2 is not None
    assert lot_2["milestones"][0]["type"] == "securityClearanceDeadline"
    assert lot_2["milestones"][0]["dueDate"] == "2019-12-01T23:59:59Z"

    lot_3 = next(
        (lot for lot in result["tender"]["lots"] if lot["id"] == "LOT-0003"),
        None,
    )
    assert lot_3 is not None
    assert "milestones" not in lot_3


if __name__ == "__main__":
    pytest.main()
