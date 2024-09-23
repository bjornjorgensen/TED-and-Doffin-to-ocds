# tests/test_bt_171_Tender.py

from ted_and_doffin_to_ocds.converters.bt_171_tender import (
    parse_tender_rank,
    merge_tender_rank,
)


def test_parse_tender_rank():
    xml_content = """
    <root xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1">
        <efac:noticeResult>
            <efac:LotTender>
                <cbc:ID schemeName="tender">TEN-0001</cbc:ID>
                <cbc:RankCode>1</cbc:RankCode>
                <efac:TenderLot>
                    <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
                </efac:TenderLot>
            </efac:LotTender>
        </efac:noticeResult>
    </root>
    """
    result = parse_tender_rank(xml_content)
    assert result == {
        "bids": {
            "details": [{"id": "TEN-0001", "rank": 1, "relatedLots": ["LOT-0001"]}],
        },
    }


def test_merge_tender_rank():
    release_json = {}
    tender_rank_data = {
        "bids": {
            "details": [{"id": "TEN-0001", "rank": 1, "relatedLots": ["LOT-0001"]}],
        },
    }
    merge_tender_rank(release_json, tender_rank_data)
    assert release_json == tender_rank_data


# Add more tests as needed
