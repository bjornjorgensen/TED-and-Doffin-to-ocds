# tests/test_BT_1711_Tender.py

from ted_and_doffin_to_ocds.converters.BT_1711_Tender import (
    parse_tender_ranked,
    merge_tender_ranked,
)


def test_parse_tender_ranked():
    xml_content = """
    <root xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
          xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1">
        <efac:NoticeResult>
            <efac:LotTender>
                <cbc:ID schemeName="tender">TEN-0001</cbc:ID>
                <efbc:TenderRankedIndicator>true</efbc:TenderRankedIndicator>
                <efac:TenderLot>
                    <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
                </efac:TenderLot>
            </efac:LotTender>
        </efac:NoticeResult>
    </root>
    """
    result = parse_tender_ranked(xml_content)
    assert result == {
        "bids": {
            "details": [
                {"id": "TEN-0001", "hasRank": True, "relatedLots": ["LOT-0001"]},
            ],
        },
    }


def test_merge_tender_ranked():
    release_json = {}
    tender_ranked_data = {
        "bids": {
            "details": [
                {"id": "TEN-0001", "hasRank": True, "relatedLots": ["LOT-0001"]},
            ],
        },
    }
    merge_tender_ranked(release_json, tender_ranked_data)
    assert release_json == tender_ranked_data


# Add more tests as needed
