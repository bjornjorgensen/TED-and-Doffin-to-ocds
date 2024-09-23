# tests/test_BT_46_Lot.py

import pytest
from ted_and_doffin_to_ocds.converters.BT_46_Lot import (
    parse_jury_member_name,
    merge_jury_member_name,
)


def test_parse_jury_member_name():
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:TenderingTerms>
                <cac:AwardingTerms>
                    <cac:TechnicalCommitteePerson>
                        <cbc:FamilyName>Mrs Pamela Smith</cbc:FamilyName>
                    </cac:TechnicalCommitteePerson>
                </cac:AwardingTerms>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </root>
    """

    result = parse_jury_member_name(xml_content)

    assert result is not None
    assert "tender" in result
    assert "lots" in result["tender"]
    assert len(result["tender"]["lots"]) == 1

    lot = result["tender"]["lots"][0]
    assert lot["id"] == "LOT-0001"
    assert "designContest" in lot
    assert "juryMembers" in lot["designContest"]
    assert len(lot["designContest"]["juryMembers"]) == 1
    assert lot["designContest"]["juryMembers"][0]["name"] == "Mrs Pamela Smith"


def test_merge_jury_member_name():
    jury_member_data = {
        "tender": {
            "lots": [
                {
                    "id": "LOT-0001",
                    "designContest": {"juryMembers": [{"name": "Mrs Pamela Smith"}]},
                },
            ],
        },
    }

    release_json = {"tender": {"lots": [{"id": "LOT-0001", "title": "Existing Lot"}]}}

    merge_jury_member_name(release_json, jury_member_data)

    assert "designContest" in release_json["tender"]["lots"][0]
    assert "juryMembers" in release_json["tender"]["lots"][0]["designContest"]
    assert len(release_json["tender"]["lots"][0]["designContest"]["juryMembers"]) == 1
    assert (
        release_json["tender"]["lots"][0]["designContest"]["juryMembers"][0]["name"]
        == "Mrs Pamela Smith"
    )


if __name__ == "__main__":
    pytest.main()
