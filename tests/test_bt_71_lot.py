# tests/test_bt_71_Lot.py

import pytest

from src.ted_and_doffin_to_ocds.converters.eforms.bt_71_lot import (
    merge_reserved_participation,
    parse_reserved_participation,
)


def test_parse_reserved_participation() -> None:
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
    assert "reservedParticipation" in result["tender"]["lots"][0]["otherRequirements"]
    assert result["tender"]["lots"][0]["otherRequirements"][
        "reservedParticipation"
    ] == ["shelteredWorkshop"]

    xml_content_pub_ser = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0002</cbc:ID>
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

    result_pub_ser = parse_reserved_participation(xml_content_pub_ser)

    assert result_pub_ser is not None
    assert "tender" in result_pub_ser
    assert "lots" in result_pub_ser["tender"]
    assert len(result_pub_ser["tender"]["lots"]) == 1
    assert result_pub_ser["tender"]["lots"][0]["id"] == "LOT-0002"
    assert "otherRequirements" in result_pub_ser["tender"]["lots"][0]
    assert (
        "reservedParticipation"
        in result_pub_ser["tender"]["lots"][0]["otherRequirements"]
    )
    assert result_pub_ser["tender"]["lots"][0]["otherRequirements"][
        "reservedParticipation"
    ] == ["publicServiceMissionOrganization"]


def test_merge_reserved_participation() -> None:
    release_json = {"tender": {"lots": [{"id": "LOT-0001", "title": "Existing Lot"}]}}

    reserved_participation_data = {
        "tender": {
            "lots": [
                {
                    "id": "LOT-0001",
                    "otherRequirements": {
                        "reservedParticipation": ["shelteredWorkshop"],
                    },
                },
            ],
        },
    }

    merge_reserved_participation(release_json, reserved_participation_data)

    assert "otherRequirements" in release_json["tender"]["lots"][0]
    assert (
        "reservedParticipation"
        in release_json["tender"]["lots"][0]["otherRequirements"]
    )
    assert release_json["tender"]["lots"][0]["otherRequirements"][
        "reservedParticipation"
    ] == ["shelteredWorkshop"]

    release_json_pub_ser = {
        "tender": {"lots": [{"id": "LOT-0002", "title": "Existing Lot 2"}]}
    }

    reserved_participation_data_pub_ser = {
        "tender": {
            "lots": [
                {
                    "id": "LOT-0002",
                    "otherRequirements": {
                        "reservedParticipation": ["publicServiceMissionOrganization"],
                    },
                },
            ],
        },
    }

    merge_reserved_participation(
        release_json_pub_ser, reserved_participation_data_pub_ser
    )

    assert "otherRequirements" in release_json_pub_ser["tender"]["lots"][0]
    assert (
        "reservedParticipation"
        in release_json_pub_ser["tender"]["lots"][0]["otherRequirements"]
    )
    assert release_json_pub_ser["tender"]["lots"][0]["otherRequirements"][
        "reservedParticipation"
    ] == ["publicServiceMissionOrganization"]


if __name__ == "__main__":
    pytest.main()
