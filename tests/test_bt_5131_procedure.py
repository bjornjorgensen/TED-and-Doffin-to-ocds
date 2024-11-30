# tests/test_bt_5131_procedure.py

from ted_and_doffin_to_ocds.converters.bt_5131_procedure import (
    merge_place_performance_city_procedure,
    parse_place_performance_city_procedure,
)


def test_parse_place_performance_city_procedure() -> None:
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProject>
            <cac:RealizedLocation>
                <cac:Address>
                    <cbc:CityName>New York</cbc:CityName>
                </cac:Address>
            </cac:RealizedLocation>
            <cac:RealizedLocation>
                <cac:Address>
                    <cbc:CityName>Los Angeles</cbc:CityName>
                </cac:Address>
            </cac:RealizedLocation>
        </cac:ProcurementProject>
    </root>
    """

    result = parse_place_performance_city_procedure(xml_content)

    assert result is not None
    assert "tender" in result
    assert "deliveryAddresses" in result["tender"]
    assert len(result["tender"]["deliveryAddresses"]) == 2
    assert result["tender"]["deliveryAddresses"][0] == {"locality": "New York"}
    assert result["tender"]["deliveryAddresses"][1] == {"locality": "Los Angeles"}


def test_parse_place_performance_city_procedure_empty() -> None:
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProject>
            <cac:RealizedLocation>
                <cac:Address>
                </cac:Address>
            </cac:RealizedLocation>
        </cac:ProcurementProject>
    </root>
    """

    result = parse_place_performance_city_procedure(xml_content)

    assert result is None


def test_merge_place_performance_city_procedure() -> None:
    existing_json = {"tender": {"deliveryAddresses": [{"postalCode": "10001"}]}}

    new_data = {
        "tender": {
            "deliveryAddresses": [
                {"locality": "New York"},
                {"locality": "Los Angeles"},
            ],
        },
    }

    merge_place_performance_city_procedure(existing_json, new_data)

    assert len(existing_json["tender"]["deliveryAddresses"]) == 3
    assert existing_json["tender"]["deliveryAddresses"][0] == {"postalCode": "10001"}
    assert existing_json["tender"]["deliveryAddresses"][1] == {"locality": "New York"}
    assert existing_json["tender"]["deliveryAddresses"][2] == {
        "locality": "Los Angeles",
    }


def test_merge_place_performance_city_procedure_update() -> None:
    existing_json = {
        "tender": {
            "deliveryAddresses": [{"locality": "New York", "postalCode": "10001"}],
        },
    }

    new_data = {
        "tender": {"deliveryAddresses": [{"locality": "New York", "region": "NY"}]},
    }

    merge_place_performance_city_procedure(existing_json, new_data)

    assert len(existing_json["tender"]["deliveryAddresses"]) == 1
    assert existing_json["tender"]["deliveryAddresses"][0] == {
        "locality": "New York",
        "postalCode": "10001",
        "region": "NY",
    }


def test_merge_place_performance_city_procedure_empty() -> None:
    existing_json = {"tender": {}}
    merge_place_performance_city_procedure(existing_json, None)
    assert existing_json == {"tender": {}}
