from src.ted_and_doffin_to_ocds.converters.eforms.bt_760_lotresult import (
    merge_received_submissions_type,
    parse_received_submissions_type,
)


def test_parse_received_submissions_type() -> None:
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
          xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1"
          xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1">
        <ext:UBLExtensions>
            <ext:UBLExtension>
                <ext:ExtensionContent>
                    <efext:EformsExtension>
                        <efac:NoticeResult>
                            <efac:LotResult>
                                <efac:TenderLot>
                                    <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
                                </efac:TenderLot>
                                <efac:ReceivedSubmissionsStatistics>
                                    <efbc:StatisticsCode listName="received-submission-type">t-esubm</efbc:StatisticsCode>
                                    <efbc:StatisticsNumeric>5</efbc:StatisticsNumeric>
                                </efac:ReceivedSubmissionsStatistics>
                            </efac:LotResult>
                        </efac:NoticeResult>
                    </efext:EformsExtension>
                </ext:ExtensionContent>
            </ext:UBLExtension>
        </ext:UBLExtensions>
    </root>
    """
    result = parse_received_submissions_type(xml_content)
    assert result is not None
    assert "bids" in result
    assert "statistics" in result["bids"]
    assert len(result["bids"]["statistics"]) == 1
    stat = result["bids"]["statistics"][0]
    assert stat["id"] == "electronicBids-LOT-0001"
    assert stat["measure"] == "electronicBids"
    assert stat["value"] == 5
    assert stat["relatedLot"] == "LOT-0001"


def test_merge_received_submissions_type() -> None:
    release_json = {"bids": {"statistics": []}}
    received_submissions_type_data = {
        "bids": {
            "statistics": [
                {
                    "id": "electronicBids-LOT-0001",
                    "measure": "electronicBids",
                    "value": 5,
                    "relatedLot": "LOT-0001",
                },
            ],
        },
    }
    merge_received_submissions_type(release_json, received_submissions_type_data)
    assert len(release_json["bids"]["statistics"]) == 1
    stat = release_json["bids"]["statistics"][0]
    assert stat["id"] == "1"
    assert stat["measure"] == "electronicBids"
    assert stat["value"] == 5
    assert stat["relatedLot"] == "LOT-0001"
