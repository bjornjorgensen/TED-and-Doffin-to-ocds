# tests/test_bt_1711_Tender.py

from src.ted_and_doffin_to_ocds.converters.eforms.bt_1711_tender import (
    merge_tender_ranked,
    parse_tender_ranked,
)


def test_parse_tender_ranked() -> None:
    xml_content = """
    <root xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
          xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1"
          xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
          xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1">
        <ext:UBLExtensions>
            <ext:UBLExtension>
                <ext:ExtensionContent>
                    <efext:EformsExtension>
                        <efac:NoticeResult>
                            <efac:LotTender>
                                <cbc:ID schemeName="tender">TEN-0001</cbc:ID>
                                <efbc:TenderRankedIndicator>true</efbc:TenderRankedIndicator>
                                <efac:TenderLot>
                                    <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
                                </efac:TenderLot>
                            </efac:LotTender>
                            <efac:LotTender>
                                <cbc:ID schemeName="tender">TEN-0002</cbc:ID>
                                <efbc:TenderRankedIndicator>false</efbc:TenderRankedIndicator>
                                <efac:TenderLot>
                                    <cbc:ID schemeName="Lot">LOT-0002</cbc:ID>
                                </efac:TenderLot>
                            </efac:LotTender>
                        </efac:NoticeResult>
                    </efext:EformsExtension>
                </ext:ExtensionContent>
            </ext:UBLExtension>
        </ext:UBLExtensions>
    </root>
    """
    result = parse_tender_ranked(xml_content)
    assert result == {
        "bids": {
            "details": [
                {"id": "TEN-0001", "hasRank": True, "relatedLots": ["LOT-0001"]},
                {"id": "TEN-0002", "hasRank": False, "relatedLots": ["LOT-0002"]},
            ],
        },
    }


def test_parse_tender_ranked_no_tenders() -> None:
    xml_content = """
    <root xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
          xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1"
          xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
          xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1">
        <ext:UBLExtensions>
            <ext:UBLExtension>
                <ext:ExtensionContent>
                    <efext:EformsExtension>
                        <efac:NoticeResult>
                            <!-- No lot tenders with ranking information -->
                        </efac:NoticeResult>
                    </efext:EformsExtension>
                </ext:ExtensionContent>
            </ext:UBLExtension>
        </ext:UBLExtensions>
    </root>
    """
    result = parse_tender_ranked(xml_content)
    assert result is None


def test_parse_tender_ranked_incomplete_data() -> None:
    xml_content = """
    <root xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
          xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1"
          xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
          xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1">
        <ext:UBLExtensions>
            <ext:UBLExtension>
                <ext:ExtensionContent>
                    <efext:EformsExtension>
                        <efac:NoticeResult>
                            <efac:LotTender>
                                <!-- Missing ID -->
                                <efbc:TenderRankedIndicator>true</efbc:TenderRankedIndicator>
                                <efac:TenderLot>
                                    <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
                                </efac:TenderLot>
                            </efac:LotTender>
                            <efac:LotTender>
                                <cbc:ID schemeName="tender">TEN-0002</cbc:ID>
                                <!-- Missing TenderRankedIndicator -->
                                <efac:TenderLot>
                                    <cbc:ID schemeName="Lot">LOT-0002</cbc:ID>
                                </efac:TenderLot>
                            </efac:LotTender>
                            <efac:LotTender>
                                <cbc:ID schemeName="tender">TEN-0003</cbc:ID>
                                <efbc:TenderRankedIndicator>true</efbc:TenderRankedIndicator>
                                <!-- Missing TenderLot -->
                            </efac:LotTender>
                            <efac:LotTender>
                                <cbc:ID schemeName="tender">TEN-0004</cbc:ID>
                                <efbc:TenderRankedIndicator>true</efbc:TenderRankedIndicator>
                                <efac:TenderLot>
                                    <!-- Missing Lot ID -->
                                </efac:TenderLot>
                            </efac:LotTender>
                        </efac:NoticeResult>
                    </efext:EformsExtension>
                </ext:ExtensionContent>
            </ext:UBLExtension>
        </ext:UBLExtensions>
    </root>
    """
    result = parse_tender_ranked(xml_content)
    assert result is None


def test_merge_tender_ranked() -> None:
    # Test with empty release JSON
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
    
    # Test with existing bids - should update existing and add new
    release_json = {
        "bids": {
            "details": [
                {"id": "TEN-0001", "value": {"amount": 1000}, "relatedLots": ["LOT-0001"]},
                {"id": "TEN-0003", "value": {"amount": 3000}, "relatedLots": ["LOT-0003"]},
            ],
        },
    }
    tender_ranked_data = {
        "bids": {
            "details": [
                {"id": "TEN-0001", "hasRank": True, "relatedLots": ["LOT-0001"]},
                {"id": "TEN-0002", "hasRank": False, "relatedLots": ["LOT-0002"]},
            ],
        },
    }
    merge_tender_ranked(release_json, tender_ranked_data)
    assert release_json == {
        "bids": {
            "details": [
                {"id": "TEN-0001", "value": {"amount": 1000}, "hasRank": True, "relatedLots": ["LOT-0001"]},
                {"id": "TEN-0003", "value": {"amount": 3000}, "relatedLots": ["LOT-0003"]},
                {"id": "TEN-0002", "hasRank": False, "relatedLots": ["LOT-0002"]},
            ],
        },
    }


def test_merge_tender_ranked_none_data() -> None:
    release_json = {"bids": {"details": []}}
    merge_tender_ranked(release_json, None)
    assert release_json == {"bids": {"details": []}}
