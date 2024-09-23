# tests/test_BT_71_Part.py

import pytest
from ted_and_doffin_to_ocds.converters.BT_71_Part import (
    parse_reserved_participation_part,
    merge_reserved_participation_part,
)


def test_parse_reserved_participation_part():
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Part">PART-0001</cbc:ID>
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
    assert "reservedParticipation" in result["tender"]["otherRequirements"]
    assert result["tender"]["otherRequirements"]["reservedParticipation"] == [
        "shelteredWorkshop",
    ]


def test_merge_reserved_participation_part():
    release_json = {"tender": {"title": "Existing Tender"}}

    reserved_participation_data = {
        "tender": {
            "otherRequirements": {"reservedParticipation": ["shelteredWorkshop"]},
        },
    }

    merge_reserved_participation_part(release_json, reserved_participation_data)

    assert "otherRequirements" in release_json["tender"]
    assert "reservedParticipation" in release_json["tender"]["otherRequirements"]
    assert release_json["tender"]["otherRequirements"]["reservedParticipation"] == [
        "shelteredWorkshop",
    ]


def test_merge_multiple_reserved_participation_part():
    release_json = {
        "tender": {
            "otherRequirements": {
                "reservedParticipation": ["publicServiceMissionOrganization"],
            },
        },
    }

    reserved_participation_data = {
        "tender": {
            "otherRequirements": {"reservedParticipation": ["shelteredWorkshop"]},
        },
    }

    merge_reserved_participation_part(release_json, reserved_participation_data)

    assert "otherRequirements" in release_json["tender"]
    assert "reservedParticipation" in release_json["tender"]["otherRequirements"]
    assert set(
        release_json["tender"]["otherRequirements"]["reservedParticipation"],
    ) == {"publicServiceMissionOrganization", "shelteredWorkshop"}


if __name__ == "__main__":
    pytest.main()
