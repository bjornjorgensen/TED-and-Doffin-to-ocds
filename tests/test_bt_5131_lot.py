# tests/test_bt_5131_Lot.py

from ted_and_doffin_to_ocds.converters.bt_5131_lot import (
    merge_place_performance_city,
    parse_place_performance_city,
)


def test_parse_place_performance_city() -> None:
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-001</cbc:ID>
            <cac:ProcurementProject>
                <cac:RealizedLocation>
                    <cac:Address>
                        <cbc:CityName>New York</cbc:CityName>
                    </cac:Address>
                </cac:RealizedLocation>
            </cac:ProcurementProject>
        </cac:ProcurementProjectLot>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-002</cbc:ID>
            <cac:ProcurementProject>
                <cac:RealizedLocation>
                    <cac:Address>
                        <cbc:CityName>Los Angeles</cbc:CityName>
                    </cac:Address>
                </cac:RealizedLocation>
                <cac:RealizedLocation>
                    <cac:Address>
                        <cbc:CityName>San Francisco</cbc:CityName>
                    </cac:Address>
                </cac:RealizedLocation>
            </cac:ProcurementProject>
        </cac:ProcurementProjectLot>
    </root>
    """

    result = parse_place_performance_city(xml_content)

    assert result is not None
    assert "tender" in result
    assert "items" in result["tender"]
    assert len(result["tender"]["items"]) == 2

    assert result["tender"]["items"][0] == {
        "id": "1",
        "relatedLot": "LOT-001",
        "deliveryAddresses": [{"locality": "New York"}],
    }

    assert result["tender"]["items"][1] == {
        "id": "2",
        "relatedLot": "LOT-002",
        "deliveryAddresses": [
            {"locality": "Los Angeles"},
            {"locality": "San Francisco"},
        ],
    }


def test_parse_place_performance_city_empty() -> None:
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-001</cbc:ID>
            <cac:ProcurementProject>
                <cac:RealizedLocation>
                    <cac:Address>
                    </cac:Address>
                </cac:RealizedLocation>
            </cac:ProcurementProject>
        </cac:ProcurementProjectLot>
    </root>
    """

    result = parse_place_performance_city(xml_content)

    assert result is None


def test_merge_place_performance_city() -> None:
    existing_json = {
        "tender": {
            "items": [
                {
                    "id": "1",
                    "relatedLot": "LOT-001",
                    "deliveryAddresses": [{"postalCode": "10001"}],
                },
            ],
        },
    }

    new_data = {
        "tender": {
            "items": [
                {
                    "id": "1",
                    "relatedLot": "LOT-001",
                    "deliveryAddresses": [{"locality": "New York"}],
                },
                {
                    "id": "2",
                    "relatedLot": "LOT-002",
                    "deliveryAddresses": [{"locality": "Los Angeles"}],
                },
            ],
        },
    }

    merge_place_performance_city(existing_json, new_data)

    assert len(existing_json["tender"]["items"]) == 2
    assert existing_json["tender"]["items"][0] == {
        "id": "1",
        "relatedLot": "LOT-001",
        "deliveryAddresses": [{"postalCode": "10001", "locality": "New York"}],
    }
    assert existing_json["tender"]["items"][1] == {
        "id": "2",
        "relatedLot": "LOT-002",
        "deliveryAddresses": [{"locality": "Los Angeles"}],
    }


def test_merge_place_performance_city_empty() -> None:
    existing_json = {"tender": {"items": []}}
    merge_place_performance_city(existing_json, None)
    assert existing_json == {"tender": {"items": []}}
