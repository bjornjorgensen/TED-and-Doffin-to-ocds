# tests/test_opt_320_lotresult.py

from src.ted_and_doffin_to_ocds.converters.eforms.opt_320_lotresult import (
    merge_tender_identifier_reference,
    parse_tender_identifier_reference,
)


def test_parse_tender_identifier_reference() -> None:
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
          xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1">
        <efac:NoticeResult>
            <efac:LotResult>
                <cbc:ID>LOT-001</cbc:ID>
                <efac:LotTender>
                    <cbc:ID schemeName="tender">TEN-0001</cbc:ID>
                </efac:LotTender>
                <efac:LotTender>
                    <cbc:ID schemeName="tender">TEN-0002</cbc:ID>
                </efac:LotTender>
                <efac:LotTender>
                    <cbc:ID schemeName="tender">TEN-0003</cbc:ID>
                </efac:LotTender>
            </efac:LotResult>
        </efac:NoticeResult>
    </root>
    """
    result = parse_tender_identifier_reference(xml_content)
    assert result == {
        "awards": [
            {
                "relatedBids": ["TEN-0001", "TEN-0002", "TEN-0003"],
                "lotID": "LOT-001"
            }
        ]
    }


def test_parse_tender_identifier_reference_with_invalid_patterns() -> None:
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
          xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1">
        <efac:NoticeResult>
            <efac:LotResult>
                <efac:LotTender>
                    <cbc:ID schemeName="tender">TEN-0001</cbc:ID>
                </efac:LotTender>
                <efac:LotTender>
                    <cbc:ID schemeName="tender">TEN-12345</cbc:ID>
                </efac:LotTender>
                <efac:LotTender>
                    <cbc:ID schemeName="tender">INVALID-ID</cbc:ID>
                </efac:LotTender>
            </efac:LotResult>
        </efac:NoticeResult>
    </root>
    """
    result = parse_tender_identifier_reference(xml_content)
    assert result == {"awards": [{"relatedBids": ["TEN-0001"]}]}


def test_parse_tender_identifier_reference_multiple_lots() -> None:
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
          xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1">
        <efac:NoticeResult>
            <efac:LotResult>
                <cbc:ID>LOT-001</cbc:ID>
                <efac:LotTender>
                    <cbc:ID schemeName="tender">TEN-0001</cbc:ID>
                </efac:LotTender>
            </efac:LotResult>
            <efac:LotResult>
                <cbc:ID>LOT-002</cbc:ID>
                <efac:LotTender>
                    <cbc:ID schemeName="tender">TEN-0002</cbc:ID>
                </efac:LotTender>
                <efac:LotTender>
                    <cbc:ID schemeName="tender">TEN-0003</cbc:ID>
                </efac:LotTender>
            </efac:LotResult>
        </efac:NoticeResult>
    </root>
    """
    result = parse_tender_identifier_reference(xml_content)
    assert result == {
        "awards": [
            {
                "relatedBids": ["TEN-0001"],
                "lotID": "LOT-001"
            },
            {
                "relatedBids": ["TEN-0002", "TEN-0003"],
                "lotID": "LOT-002"
            }
        ]
    }


def test_merge_tender_identifier_reference() -> None:
    release_json = {"awards": [{"id": "AWD-0001", "title": "Existing Award"}]}
    tender_identifier_data = {
        "awards": [{"relatedBids": ["TEN-0001", "TEN-0002", "TEN-0003"]}]
    }
    merge_tender_identifier_reference(release_json, tender_identifier_data)
    assert release_json == {
        "awards": [
            {
                "id": "AWD-0001",
                "title": "Existing Award",
                "relatedBids": ["TEN-0001", "TEN-0002", "TEN-0003"],
            }
        ]
    }


def test_merge_tender_identifier_reference_no_existing_awards() -> None:
    release_json = {}
    tender_identifier_data = {
        "awards": [{"relatedBids": ["TEN-0001", "TEN-0002", "TEN-0003"]}]
    }
    merge_tender_identifier_reference(release_json, tender_identifier_data)
    assert release_json == {
        "awards": [{"relatedBids": ["TEN-0001", "TEN-0002", "TEN-0003"]}]
    }


def test_merge_tender_identifier_reference_no_data() -> None:
    release_json = {"awards": [{"id": "AWD-0001", "title": "Existing Award"}]}
    merge_tender_identifier_reference(release_json, None)
    assert release_json == {"awards": [{"id": "AWD-0001", "title": "Existing Award"}]}
