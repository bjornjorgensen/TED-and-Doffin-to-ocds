from ted_and_doffin_to_ocds.converters.bt_711_lotresult import (
    parse_tender_value_highest,
    merge_tender_value_highest,
)


def test_parse_tender_value_highest():
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1">
        <efac:noticeResult>
            <efac:LotResult>
                <efac:TenderLot>
                    <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
                </efac:TenderLot>
                <cbc:HigherTenderAmount currencyID="EUR">20000.00</cbc:HigherTenderAmount>
            </efac:LotResult>
        </efac:noticeResult>
    </root>
    """
    result = parse_tender_value_highest(xml_content)
    assert result is not None
    assert "bids" in result
    assert "statistics" in result["bids"]
    assert len(result["bids"]["statistics"]) == 1
    stat = result["bids"]["statistics"][0]
    assert stat["id"] == "highest-LOT-0001"
    assert stat["measure"] == "highestValidBidValue"
    assert stat["value"]["amount"] == 20000.00
    assert stat["value"]["currency"] == "EUR"
    assert stat["relatedLots"] == ["LOT-0001"]


def test_merge_tender_value_highest():
    release_json = {"bids": {"statistics": []}}
    tender_value_highest_data = {
        "bids": {
            "statistics": [
                {
                    "id": "highest-LOT-0001",
                    "measure": "highestValidBidValue",
                    "value": {"amount": 20000.00, "currency": "EUR"},
                    "relatedLots": ["LOT-0001"],
                },
            ],
        },
    }
    merge_tender_value_highest(release_json, tender_value_highest_data)
    assert len(release_json["bids"]["statistics"]) == 1
    stat = release_json["bids"]["statistics"][0]
    assert stat["id"] == "1"
    assert stat["measure"] == "highestValidBidValue"
    assert stat["value"]["amount"] == 20000.00
    assert stat["value"]["currency"] == "EUR"
    assert stat["relatedLots"] == ["LOT-0001"]