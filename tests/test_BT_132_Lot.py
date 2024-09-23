# tests/test_BT_132_Lot.py

import pytest
from ted_and_doffin_to_ocds.converters.BT_132_Lot import (
    parse_lot_public_opening_date,
    merge_lot_public_opening_date,
)


def test_parse_lot_public_opening_date():
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:TenderingProcess>
                <cac:OpenTenderEvent>
                    <cbc:OccurrenceDate>2019-11-05+01:00</cbc:OccurrenceDate>
                    <cbc:OccurrenceTime>14:00:00+01:00</cbc:OccurrenceTime>
                </cac:OpenTenderEvent>
            </cac:TenderingProcess>
        </cac:ProcurementProjectLot>
    </root>
    """

    result = parse_lot_public_opening_date(xml_content)

    assert result is not None
    assert len(result["tender"]["lots"]) == 1
    assert result["tender"]["lots"][0]["id"] == "LOT-0001"
    assert (
        result["tender"]["lots"][0]["awardPeriod"]["startDate"]
        == "2019-11-05T14:00:00+01:00"
    )
    assert (
        result["tender"]["lots"][0]["bidOpening"]["date"] == "2019-11-05T14:00:00+01:00"
    )


def test_merge_lot_public_opening_date():
    release_json = {"tender": {"lots": [{"id": "LOT-0001", "title": "Existing Lot"}]}}

    lot_public_opening_date_data = {
        "tender": {
            "lots": [
                {
                    "id": "LOT-0001",
                    "awardPeriod": {"startDate": "2019-11-05T14:00:00+01:00"},
                    "bidOpening": {"date": "2019-11-05T14:00:00+01:00"},
                },
            ],
        },
    }

    merge_lot_public_opening_date(release_json, lot_public_opening_date_data)

    assert len(release_json["tender"]["lots"]) == 1
    assert release_json["tender"]["lots"][0]["id"] == "LOT-0001"
    assert release_json["tender"]["lots"][0]["title"] == "Existing Lot"
    assert (
        release_json["tender"]["lots"][0]["awardPeriod"]["startDate"]
        == "2019-11-05T14:00:00+01:00"
    )
    assert (
        release_json["tender"]["lots"][0]["bidOpening"]["date"]
        == "2019-11-05T14:00:00+01:00"
    )


if __name__ == "__main__":
    pytest.main()
