# tests/test_bt_71_part.py

import pytest
from ted_and_doffin_to_ocds.converters.bt_71_part import (
    parse_reserved_participation_part,
    merge_reserved_participation_part,
)


def test_parse_reserved_participation_part():
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="part">PART-0001</cbc:ID>
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

    result = parse_reserved_participation_part(xml_content)

    assert result is not None
    assert "tender" in result
    assert "otherRequirements" in result["tender"]
    assert "reservedparticipation" in result["tender"]["otherRequirements"]
    assert result["tender"]["otherRequirements"]["reservedparticipation"] == [
        "shelteredWorkshop",
    ]


def test_merge_reserved_participation_part():
    release_json = {"tender": {"title": "Existing Tender"}}

    reserved_participation_data = {
        "tender": {
            "otherRequirements": {"reservedparticipation": ["shelteredWorkshop"]},
        },
    }

    merge_reserved_participation_part(release_json, reserved_participation_data)

    assert "otherRequirements" in release_json["tender"]
    assert "reservedparticipation" in release_json["tender"]["otherRequirements"]
    assert release_json["tender"]["otherRequirements"]["reservedparticipation"] == [
        "shelteredWorkshop",
    ]


def test_merge_multiple_reserved_participation_part():
    release_json = {
        "tender": {
            "otherRequirements": {
                "reservedparticipation": ["publicServiceMissionorganization"],
            },
        },
    }

    reserved_participation_data = {
        "tender": {
            "otherRequirements": {"reservedparticipation": ["shelteredWorkshop"]},
        },
    }

    merge_reserved_participation_part(release_json, reserved_participation_data)

    assert "otherRequirements" in release_json["tender"]
    assert "reservedparticipation" in release_json["tender"]["otherRequirements"]
    assert set(
        release_json["tender"]["otherRequirements"]["reservedparticipation"],
    ) == {"publicServiceMissionorganization", "shelteredWorkshop"}


if __name__ == "__main__":
    pytest.main()
