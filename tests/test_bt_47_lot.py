# tests/test_bt_47_Lot.py

import pytest

from src.ted_and_doffin_to_ocds.converters.eforms.bt_47_lot import (
    merge_participant_name,
    parse_participant_name,
)


def test_parse_participant_name() -> None:
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:TenderingTerms>
                <cac:EconomicOperatorShortList>
                    <cac:PreSelectedParty>
                        <cac:PartyName>
                            <cbc:Name>Mr P. Sanchez</cbc:Name>
                        </cac:PartyName>
                    </cac:PreSelectedParty>
                </cac:EconomicOperatorShortList>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </root>
    """

    result = parse_participant_name(xml_content)

    assert result is not None
    assert "parties" in result
    assert "tender" in result
    assert "lots" in result["tender"]
    assert len(result["parties"]) == 1
    assert len(result["tender"]["lots"]) == 1

    party = result["parties"][0]
    assert party["id"] == "1"
    assert party["name"] == "Mr P. Sanchez"
    assert party["roles"] == ["selectedParticipant"]

    lot = result["tender"]["lots"][0]
    assert lot["id"] == "LOT-0001"
    assert "designContest" in lot
    assert "selectedParticipants" in lot["designContest"]
    assert len(lot["designContest"]["selectedParticipants"]) == 1
    assert lot["designContest"]["selectedParticipants"][0]["id"] == "1"
    assert lot["designContest"]["selectedParticipants"][0]["name"] == "Mr P. Sanchez"


def test_merge_participant_name() -> None:
    participant_data = {
        "parties": [
            {"id": "1", "name": "Mr P. Sanchez", "roles": ["selectedParticipant"]},
        ],
        "tender": {
            "lots": [
                {
                    "id": "LOT-0001",
                    "designContest": {
                        "selectedParticipants": [{"id": "1", "name": "Mr P. Sanchez"}],
                    },
                },
            ],
        },
    }

    release_json = {
        "parties": [],
        "tender": {"lots": [{"id": "LOT-0001", "title": "Existing Lot"}]},
    }

    merge_participant_name(release_json, participant_data)

    assert len(release_json["parties"]) == 1
    assert release_json["parties"][0]["name"] == "Mr P. Sanchez"
    assert release_json["parties"][0]["roles"] == ["selectedParticipant"]

    assert "designContest" in release_json["tender"]["lots"][0]
    assert "selectedParticipants" in release_json["tender"]["lots"][0]["designContest"]
    assert (
        len(release_json["tender"]["lots"][0]["designContest"]["selectedParticipants"])
        == 1
    )
    assert (
        release_json["tender"]["lots"][0]["designContest"]["selectedParticipants"][0][
            "name"
        ]
        == "Mr P. Sanchez"
    )


if __name__ == "__main__":
    pytest.main()
