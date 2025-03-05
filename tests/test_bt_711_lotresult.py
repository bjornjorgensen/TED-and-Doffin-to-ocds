from src.ted_and_doffin_to_ocds.converters.eforms.bt_711_lotresult import (
    merge_tender_value_highest,
    parse_tender_value_highest,
)


def test_parse_tender_value_highest() -> None:
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1">
        <efac:NoticeResult>
            <efac:LotResult>
                <efac:TenderLot>
                    <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
                </efac:TenderLot>
                <cbc:HigherTenderAmount currencyID="EUR">20000.00</cbc:HigherTenderAmount>
            </efac:LotResult>
        </efac:NoticeResult>
    </root>
    """
    result = parse_tender_value_highest(xml_content)
    assert result is not None
    assert "bids" in result
    assert "statistics" in result["bids"]
    assert len(result["bids"]["statistics"]) == 1
    stat = result["bids"]["statistics"][0]
    assert stat["id"] == "1"
    assert stat["measure"] == "highestValidBidValue"
    assert stat["value"] == 20000.00
    assert stat["currency"] == "EUR"
    assert stat["relatedLot"] == "LOT-0001"


def test_merge_tender_value_highest() -> None:
    release_json = {"bids": {"statistics": []}}
    tender_value_highest_data = {
        "bids": {
            "statistics": [
                {
                    "id": "1",
                    "measure": "highestValidBidValue",
                    "value": 20000.00,
                    "currency": "EUR",
                    "relatedLot": "LOT-0001",
                },
            ],
        },
    }
    merge_tender_value_highest(release_json, tender_value_highest_data)
    assert len(release_json["bids"]["statistics"]) == 1
    stat = release_json["bids"]["statistics"][0]
    assert stat["id"] == "1"
    assert stat["measure"] == "highestValidBidValue"
    assert stat["value"] == 20000.00
    assert stat["currency"] == "EUR"
    assert stat["relatedLot"] == "LOT-0001"
