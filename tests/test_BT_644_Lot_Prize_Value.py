# tests/test_BT_644_Lot_Prize_Value.py

from converters.BT_644_Lot_Prize_Value import (
    parse_lot_prize_value,
    merge_lot_prize_value,
)


def test_parse_lot_prize_value():
    xml_content = b"""
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:TenderingTerms>
                <cac:AwardingTerms>
                    <cac:Prize>
                        <cbc:ValueAmount currencyID="EUR">5000</cbc:ValueAmount>
                    </cac:Prize>
                    <cac:Prize>
                        <cbc:ValueAmount currencyID="EUR">3000</cbc:ValueAmount>
                    </cac:Prize>
                </cac:AwardingTerms>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </root>
    """

    result = parse_lot_prize_value(xml_content)

    assert result is not None
    assert len(result["tender"]["lots"]) == 1
    lot = result["tender"]["lots"][0]
    assert lot["id"] == "LOT-0001"
    assert len(lot["designContest"]["prizes"]["details"]) == 2
    assert lot["designContest"]["prizes"]["details"][0]["value"]["amount"] == 5000
    assert lot["designContest"]["prizes"]["details"][0]["value"]["currency"] == "EUR"
    assert lot["designContest"]["prizes"]["details"][1]["value"]["amount"] == 3000
    assert lot["designContest"]["prizes"]["details"][1]["value"]["currency"] == "EUR"


def test_parse_lot_prize_value_no_data():
    xml_content = b"""
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
        </cac:ProcurementProjectLot>
    </root>
    """

    result = parse_lot_prize_value(xml_content)

    assert result is None


def test_merge_lot_prize_value():
    existing_release = {
        "tender": {
            "lots": [
                {
                    "id": "LOT-0001",
                    "designContest": {
                        "prizes": {
                            "details": [
                                {
                                    "id": "0",
                                    "value": {"amount": 1000, "currency": "USD"},
                                }
                            ]
                        }
                    },
                }
            ]
        }
    }

    new_data = {
        "tender": {
            "lots": [
                {
                    "id": "LOT-0001",
                    "designContest": {
                        "prizes": {
                            "details": [
                                {
                                    "id": "0",
                                    "value": {"amount": 5000, "currency": "EUR"},
                                },
                                {
                                    "id": "1",
                                    "value": {"amount": 3000, "currency": "EUR"},
                                },
                            ]
                        }
                    },
                }
            ]
        }
    }

    merge_lot_prize_value(existing_release, new_data)

    assert len(existing_release["tender"]["lots"]) == 1
    lot = existing_release["tender"]["lots"][0]
    assert len(lot["designContest"]["prizes"]["details"]) == 2
    assert lot["designContest"]["prizes"]["details"][0]["value"]["amount"] == 5000
    assert lot["designContest"]["prizes"]["details"][0]["value"]["currency"] == "EUR"
    assert lot["designContest"]["prizes"]["details"][1]["value"]["amount"] == 3000
    assert lot["designContest"]["prizes"]["details"][1]["value"]["currency"] == "EUR"


def test_merge_lot_prize_value_new_lot():
    existing_release = {"tender": {"lots": []}}

    new_data = {
        "tender": {
            "lots": [
                {
                    "id": "LOT-0001",
                    "designContest": {
                        "prizes": {
                            "details": [
                                {
                                    "id": "0",
                                    "value": {"amount": 5000, "currency": "EUR"},
                                }
                            ]
                        }
                    },
                }
            ]
        }
    }

    merge_lot_prize_value(existing_release, new_data)

    assert len(existing_release["tender"]["lots"]) == 1
    lot = existing_release["tender"]["lots"][0]
    assert lot["id"] == "LOT-0001"
    assert len(lot["designContest"]["prizes"]["details"]) == 1
    assert lot["designContest"]["prizes"]["details"][0]["value"]["amount"] == 5000
    assert lot["designContest"]["prizes"]["details"][0]["value"]["currency"] == "EUR"
