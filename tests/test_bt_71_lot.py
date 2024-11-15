# tests/test_bt_71_Lot.py

import pytest
from ted_and_doffin_to_ocds.converters.bt_71_lot import (
    parse_reserved_participation,
    merge_reserved_participation,
)


def test_parse_reserved_participation():
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:TenderingTerms>
                <cac:TendererQualificationRequest>
                    <cac:SpecificTendererRequirement>
                        <cbc:TendererRequirementTypeCode listName="reserved-procurement">res-ws</cbc:TendererRequirementTypeCode>
                    </cac:SpecificTendererRequirement>
                </cac:TendererQualificationRequest>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </root>
    """

    result = parse_reserved_participation(xml_content)

    assert result is not None
    assert "tender" in result
    assert "lots" in result["tender"]
    assert len(result["tender"]["lots"]) == 1
    assert result["tender"]["lots"][0]["id"] == "LOT-0001"
    assert "otherRequirements" in result["tender"]["lots"][0]
    assert "reservedparticipation" in result["tender"]["lots"][0]["otherRequirements"]
    assert result["tender"]["lots"][0]["otherRequirements"][
        "reservedparticipation"
    ] == ["shelteredWorkshop"]


def test_merge_reserved_participation():
    release_json = {"tender": {"lots": [{"id": "LOT-0001", "title": "Existing Lot"}]}}

    reserved_participation_data = {
        "tender": {
            "lots": [
                {
                    "id": "LOT-0001",
                    "otherRequirements": {
                        "reservedparticipation": ["shelteredWorkshop"],
                    },
                },
            ],
        },
    }

    merge_reserved_participation(release_json, reserved_participation_data)

    assert "otherRequirements" in release_json["tender"]["lots"][0]
    assert (
        "reservedparticipation"
        in release_json["tender"]["lots"][0]["otherRequirements"]
    )
    assert release_json["tender"]["lots"][0]["otherRequirements"][
        "reservedparticipation"
    ] == ["shelteredWorkshop"]


if __name__ == "__main__":
    pytest.main()
