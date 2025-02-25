# tests/test_bt_71_part.py

import pytest

from src.ted_and_doffin_to_ocds.converters.eforms.bt_71_part import (
    RESERVED_CODE_MAPPING,
    merge_reserved_participation_part,
    parse_reserved_participation_part,
)


def test_parse_reserved_participation_part() -> None:
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

    xml_content_pub_ser = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Part">PART-0002</cbc:ID>
            <cac:TenderingTerms>
                <cac:TendererQualificationRequest>
                    <cac:SpecificTendererRequirement>
                        <cbc:TendererRequirementTypeCode listName="reserved-procurement">res-pub-ser</cbc:TendererRequirementTypeCode>
                    </cac:SpecificTendererRequirement>
                </cac:TendererQualificationRequest>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </root>
    """

    result_pub_ser = parse_reserved_participation_part(xml_content_pub_ser)

    assert result_pub_ser is not None
    assert "tender" in result_pub_ser
    assert "otherRequirements" in result_pub_ser["tender"]
    assert "reservedParticipation" in result_pub_ser["tender"]["otherRequirements"]
    assert result_pub_ser["tender"]["otherRequirements"]["reservedParticipation"] == [
        "publicServiceMissionOrganization",
    ]


def test_parse_reserved_participation_part_invalid_input():
    """Test parsing with invalid input data."""
    assert parse_reserved_participation_part("") is None
    assert parse_reserved_participation_part("<invalid>xml</invalid>") is None
    assert parse_reserved_participation_part(None) is None


def test_parse_reserved_participation_part_no_matches():
    """Test parsing XML without any reserved participation codes."""
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Part">PART-0001</cbc:ID>
            <cac:TenderingTerms/>
        </cac:ProcurementProjectLot>
    </root>
    """
    assert parse_reserved_participation_part(xml_content) is None


def test_parse_reserved_participation_part_unknown_code():
    """Test parsing XML with unknown reservation code."""
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Part">PART-0001</cbc:ID>
            <cac:TenderingTerms>
                <cac:TendererQualificationRequest>
                    <cac:SpecificTendererRequirement>
                        <cbc:TendererRequirementTypeCode listName="reserved-procurement">unknown-code</cbc:TendererRequirementTypeCode>
                    </cac:SpecificTendererRequirement>
                </cac:TendererQualificationRequest>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </root>
    """
    assert parse_reserved_participation_part(xml_content) is None


def test_merge_reserved_participation_part() -> None:
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


def test_merge_multiple_reserved_participation_part() -> None:
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


def test_merge_reserved_participation_part_none_data():
    """Test merging with None data."""
    release_json = {"tender": {}}
    merge_reserved_participation_part(release_json, None)
    assert "otherRequirements" not in release_json["tender"]


def test_merge_reserved_participation_part_empty_release():
    """Test merging into empty release JSON."""
    release_json = {}
    data = {
        "tender": {
            "otherRequirements": {"reservedParticipation": ["shelteredWorkshop"]},
        },
    }
    merge_reserved_participation_part(release_json, data)
    assert "tender" in release_json
    assert "otherRequirements" in release_json["tender"]
    assert release_json["tender"]["otherRequirements"]["reservedParticipation"] == [
        "shelteredWorkshop"
    ]


def test_reserved_code_mapping_consistency():
    """Test that RESERVED_CODE_MAPPING contains expected mappings."""
    assert RESERVED_CODE_MAPPING["res-pub-ser"] == "publicServiceMissionOrganization"
    assert RESERVED_CODE_MAPPING["res-ws"] == "shelteredWorkshop"
    assert len(RESERVED_CODE_MAPPING) == 2


if __name__ == "__main__":
    pytest.main()
