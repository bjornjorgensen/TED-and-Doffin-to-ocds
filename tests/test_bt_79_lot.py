# tests/test_bt_79_Lot.py

import pytest
from ted_and_doffin_to_ocds.converters.bt_79_lot import (
    parse_performing_staff_qualification,
    merge_performing_staff_qualification,
)
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.ted_and_doffin_to_ocds.main import main


def test_parse_performing_staff_qualification():
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:TenderingTerms>
                <cbc:RequiredCurriculaCode listName="requirement-stage">t-requ</cbc:RequiredCurriculaCode>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </root>
    """

    result = parse_performing_staff_qualification(xml_content)

    assert result is not None
    assert "tender" in result
    assert "lots" in result["tender"]
    assert len(result["tender"]["lots"]) == 1
    assert result["tender"]["lots"][0]["id"] == "LOT-0001"
    assert "otherRequirements" in result["tender"]["lots"][0]
    assert (
        result["tender"]["lots"][0]["otherRequirements"][
            "requiresStaffNamesAndQualifications"
        ]
        is True
    )


def test_merge_performing_staff_qualification():
    release_json = {"tender": {"lots": [{"id": "LOT-0001", "title": "Existing Lot"}]}}

    staff_qualification_data = {
        "tender": {
            "lots": [
                {
                    "id": "LOT-0001",
                    "otherRequirements": {"requiresStaffNamesAndQualifications": True},
                },
            ],
        },
    }

    merge_performing_staff_qualification(release_json, staff_qualification_data)

    assert "otherRequirements" in release_json["tender"]["lots"][0]
    assert (
        release_json["tender"]["lots"][0]["otherRequirements"][
            "requiresStaffNamesAndQualifications"
        ]
        is True
    )


def test_bt_79_lot_performing_staff_qualification_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:TenderingTerms>
                <cbc:RequiredCurriculaCode listName="requirement-stage">t-requ</cbc:RequiredCurriculaCode>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0002</cbc:ID>
            <cac:TenderingTerms>
                <cbc:RequiredCurriculaCode listName="requirement-stage">not-requ</cbc:RequiredCurriculaCode>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0003</cbc:ID>
            <cac:TenderingTerms>
                <cbc:RequiredCurriculaCode listName="requirement-stage">other-code</cbc:RequiredCurriculaCode>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </root>
    """
    xml_file = tmp_path / "test_input_performing_staff_qualification.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open("output.json") as f:
        result = json.load(f)

    assert "tender" in result
    assert "lots" in result["tender"]

    lots_with_requirements = [
        lot for lot in result["tender"]["lots"] if "otherRequirements" in lot
    ]
    assert len(lots_with_requirements) == 2

    lot_1 = next(
        (lot for lot in lots_with_requirements if lot["id"] == "LOT-0001"),
        None,
    )
    assert lot_1 is not None
    assert lot_1["otherRequirements"]["requiresStaffNamesAndQualifications"] is True

    lot_2 = next(
        (lot for lot in lots_with_requirements if lot["id"] == "LOT-0002"),
        None,
    )
    assert lot_2 is not None
    assert lot_2["otherRequirements"]["requiresStaffNamesAndQualifications"] is False

    lot_3 = next(
        (lot for lot in result["tender"]["lots"] if lot["id"] == "LOT-0003"),
        None,
    )
    assert lot_3 is not None
    assert "otherRequirements" not in lot_3


if __name__ == "__main__":
    pytest.main()
