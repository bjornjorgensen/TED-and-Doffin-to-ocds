import pytest

from ted_and_doffin_to_ocds.converters.bt_27_part import (
    merge_bt_27_part,
    parse_bt_27_part,
)


@pytest.fixture
def sample_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8"?>
    <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
                         xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
                         xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Part">PART-0001</cbc:ID>
            <cac:ProcurementProject>
                <cac:RequestedTenderTotal>
                    <cbc:EstimatedOverallContractAmount currencyID="EUR">250000</cbc:EstimatedOverallContractAmount>
                </cac:RequestedTenderTotal>
            </cac:ProcurementProject>
        </cac:ProcurementProjectLot>
    </ContractAwardNotice>
    """


def test_parse_bt_27_part_success(sample_xml: str) -> None:
    result = parse_bt_27_part(sample_xml)

    assert "tender" in result
    assert "value" in result["tender"]
    assert result["tender"]["value"]["amount"] == 250000.0
    assert result["tender"]["value"]["currency"] == "EUR"


def test_parse_bt_27_part_no_value() -> None:
    xml_without_value = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
                         xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
                         xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Part">PART-0001</cbc:ID>
        </cac:ProcurementProjectLot>
    </ContractAwardNotice>
    """
    result = parse_bt_27_part(xml_without_value)

    assert "tender" in result
    assert "value" not in result["tender"]


def test_merge_bt_27_part(sample_xml: str) -> None:
    parsed_data = parse_bt_27_part(sample_xml)
    release_json = {}

    merge_bt_27_part(release_json, parsed_data)

    assert "tender" in release_json
    assert "value" in release_json["tender"]
    assert release_json["tender"]["value"]["amount"] == 250000.0
    assert release_json["tender"]["value"]["currency"] == "EUR"


def test_merge_bt_27_part_no_value() -> None:
    release_json = {}
    bt_27_part_data = {"tender": {}}

    merge_bt_27_part(release_json, bt_27_part_data)

    assert release_json == {}
