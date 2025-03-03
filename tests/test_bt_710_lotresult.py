from src.ted_and_doffin_to_ocds.converters.eforms.bt_710_lotresult import (
    merge_tender_value_lowest,
    parse_tender_value_lowest,
)

def test_parse_tender_value_lowest() -> None:
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
    assert stat["measure"] == "lowestValidBidValue"
    assert stat["value"] == 10000.00
    assert stat["currency"] == "EUR"
    assert stat["relatedLot"] == "LOT-0001"
    assert stat["id"] == "1"

def test_parse_tender_value_lowest_multiple_lots() -> None:
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
            <efac:LotResult>
                <efac:TenderLot>
                    <cbc:ID schemeName="Lot">LOT-0002</cbc:ID>
                </efac:TenderLot>
                <cbc:LowerTenderAmount currencyID="USD">15000.00</cbc:LowerTenderAmount>
            </efac:LotResult>
        </efac:NoticeResult>
    </root>
    """
    result = parse_tender_value_lowest(xml_content)
    assert result is not None
    assert "bids" in result
    assert "statistics" in result["bids"]
    assert len(result["bids"]["statistics"]) == 2
    
    stat1 = result["bids"]["statistics"][0]
    assert stat1["measure"] == "lowestValidBidValue"
    assert stat1["value"] == 10000.00
    assert stat1["currency"] == "EUR"
    assert stat1["relatedLot"] == "LOT-0001"
    assert stat1["id"] == "1"
    
    stat2 = result["bids"]["statistics"][1]
    assert stat2["measure"] == "lowestValidBidValue"
    assert stat2["value"] == 15000.00
    assert stat2["currency"] == "USD"
    assert stat2["relatedLot"] == "LOT-0002"
    assert stat2["id"] == "2"

def test_merge_tender_value_lowest_with_existing_stats() -> None:
    release_json = {"bids": {"statistics": [
        {
            "id": "1",
            "measure": "otherMeasure",
            "value": 5000.00,
            "currency": "NOK",
        }
    ]}}
    tender_value_lowest_data = {
        "bids": {
            "statistics": [
                {
                    "id": "1",
                    "measure": "lowestValidBidValue",
                    "value": 10000.00,
                    "currency": "EUR",
                    "relatedLot": "LOT-0001",
                },
            ],
        },
    }
    merge_tender_value_lowest(release_json, tender_value_lowest_data)
    assert len(release_json["bids"]["statistics"]) == 2
    
    other_measure_stats = [s for s in release_json["bids"]["statistics"] if s["measure"] == "otherMeasure"]
    lowest_value_stats = [s for s in release_json["bids"]["statistics"] if s["measure"] == "lowestValidBidValue"]
    
    assert len(other_measure_stats) == 1
    assert len(lowest_value_stats) == 1
    
    stat_other = other_measure_stats[0]
    assert stat_other["value"] == 5000.00
    assert stat_other["currency"] == "NOK"
    assert stat_other["id"] == "1"
    
    stat_lowest = lowest_value_stats[0]
    assert stat_lowest["value"] == 10000.00
    assert stat_lowest["currency"] == "EUR"
    assert stat_lowest["relatedLot"] == "LOT-0001"
    assert stat_lowest["id"] == "2"

def test_merge_tender_value_lowest() -> None:
    release_json = {"bids": {"statistics": []}}
    tender_value_lowest_data = {
        "bids": {
            "statistics": [
                {
                    "id": "1",
                    "measure": "lowestValidBidValue",
                    "value": 10000.00,
                    "currency": "EUR",
                    "relatedLot": "LOT-0001",
                },
            ],
        },
    }
    merge_tender_value_lowest(release_json, tender_value_lowest_data)
    assert len(release_json["bids"]["statistics"]) == 1
    stat = release_json["bids"]["statistics"][0]
    assert stat["measure"] == "lowestValidBidValue"
    assert stat["value"] == 10000.00
    assert stat["currency"] == "EUR"
    assert stat["relatedLot"] == "LOT-0001"
    assert stat["id"] == "1"
