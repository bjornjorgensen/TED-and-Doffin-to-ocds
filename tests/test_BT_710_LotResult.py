from ted_and_doffin_to_ocds.converters.BT_710_LotResult import (
    parse_tender_value_lowest,
    merge_tender_value_lowest,
)


def test_parse_tender_value_lowest():
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1">
        <efac:NoticeResult>
            <efac:LotResult>
                <efac:TenderLot>
                    <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
                </efac:TenderLot>
                <cbc:LowerTenderAmount currencyID="EUR">10000.00</cbc:LowerTenderAmount>
            </efac:LotResult>
        </efac:NoticeResult>
    </root>
    """
    result = parse_tender_value_lowest(xml_content)
    assert result is not None
    assert "bids" in result
    assert "statistics" in result["bids"]
    assert len(result["bids"]["statistics"]) == 1
    stat = result["bids"]["statistics"][0]
    assert stat["id"] == "lowest-LOT-0001"
    assert stat["measure"] == "lowestValidBidValue"
    assert stat["value"]["amount"] == 10000.00
    assert stat["value"]["currency"] == "EUR"
    assert stat["relatedLots"] == ["LOT-0001"]


def test_merge_tender_value_lowest():
    release_json = {"bids": {"statistics": []}}
    tender_value_lowest_data = {
        "bids": {
            "statistics": [
                {
                    "id": "lowest-LOT-0001",
                    "measure": "lowestValidBidValue",
                    "value": {"amount": 10000.00, "currency": "EUR"},
                    "relatedLots": ["LOT-0001"],
                }
            ]
        }
    }
    merge_tender_value_lowest(release_json, tender_value_lowest_data)
    assert len(release_json["bids"]["statistics"]) == 1
    stat = release_json["bids"]["statistics"][0]
    assert stat["id"] == "1"
    assert stat["measure"] == "lowestValidBidValue"
    assert stat["value"]["amount"] == 10000.00
    assert stat["value"]["currency"] == "EUR"
    assert stat["relatedLots"] == ["LOT-0001"]
