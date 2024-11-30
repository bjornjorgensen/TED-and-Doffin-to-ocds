# tests/test_bt_712a_lotresult.py

import pytest
from lxml import etree

from ted_and_doffin_to_ocds.converters.bt_712a_lotresult import (
    merge_buyer_review_complainants_code,
    parse_buyer_review_complainants_code,
)

NAMESPACES = {
    "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
    "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    "efbc": "http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1",
}


def create_xml_content(lot_data):
    root = etree.Element("root", nsmap=NAMESPACES)
    notice_result = etree.SubElement(root, f"{{{NAMESPACES['efac']}}}NoticeResult")

    for lot_id, code in lot_data.items():
        lot_result = etree.SubElement(
            notice_result, f"{{{NAMESPACES['efac']}}}LotResult"
        )
        tender_lot = etree.SubElement(lot_result, f"{{{NAMESPACES['efac']}}}TenderLot")
        id_elem = etree.SubElement(
            tender_lot, f"{{{NAMESPACES['cbc']}}}ID", schemeName="Lot"
        )
        id_elem.text = lot_id

        appeal_stats = etree.SubElement(
            lot_result, f"{{{NAMESPACES['efac']}}}AppealRequestsStatistics"
        )
        stats_code = etree.SubElement(
            appeal_stats,
            f"{{{NAMESPACES['efbc']}}}StatisticsCode",
            listName="review-type",
        )
        stats_code.text = code

    return etree.tostring(root)


def test_parse_buyer_review_complainants_code() -> None:
    xml_content = create_xml_content({"LOT-001": "complainants", "LOT-002": "other"})
    result = parse_buyer_review_complainants_code(xml_content)

    assert result is not None
    assert "statistics" in result
    assert len(result["statistics"]) == 1

    assert result["statistics"][0] == {
        "id": "1",
        "measure": "complainants",
        "relatedLot": "LOT-001",
    }


def test_parse_buyer_review_complainants_code_no_data() -> None:
    xml_content = "<root></root>"
    result = parse_buyer_review_complainants_code(xml_content)
    assert result is None


def test_parse_buyer_review_complainants_code_missing_lot_id() -> None:
    xml_content = create_xml_content({"": "complainants"})
    result = parse_buyer_review_complainants_code(xml_content)
    assert result is None


def test_merge_buyer_review_complainants_code() -> None:
    release_json = {"statistics": []}
    complainants_code_data = {
        "statistics": [{"id": "1", "measure": "complainants", "relatedLot": "LOT-001"}]
    }

    merge_buyer_review_complainants_code(release_json, complainants_code_data)

    assert len(release_json["statistics"]) == 1
    assert release_json["statistics"][0] == complainants_code_data["statistics"][0]


def test_merge_buyer_review_complainants_code_update_existing() -> None:
    release_json = {
        "statistics": [
            {"id": "1", "measure": "complainants", "relatedLot": "LOT-001", "value": 2}
        ]
    }
    complainants_code_data = {
        "statistics": [{"id": "2", "measure": "complainants", "relatedLot": "LOT-001"}]
    }

    merge_buyer_review_complainants_code(release_json, complainants_code_data)

    assert len(release_json["statistics"]) == 1
    assert release_json["statistics"][0]["id"] == "2"
    assert "value" not in release_json["statistics"][0]
    assert release_json["statistics"][0] == {
        "id": "2",
        "measure": "complainants",
        "relatedLot": "LOT-001",
    }


def test_merge_buyer_review_complainants_code_no_data() -> None:
    release_json = {"statistics": []}
    merge_buyer_review_complainants_code(release_json, None)
    assert "statistics" in release_json
    assert len(release_json["statistics"]) == 0


@pytest.fixture
def sample_xml_content():
    return create_xml_content({"LOT-001": "complainants", "LOT-002": "complainants"})


def test_integration(sample_xml_content) -> None:
    # Parse the XML content
    parsed_data = parse_buyer_review_complainants_code(sample_xml_content)
    assert parsed_data is not None

    # Create a mock release JSON
    release_json = {"statistics": []}

    # Merge the parsed data into the release JSON
    merge_buyer_review_complainants_code(release_json, parsed_data)

    # Check the final result
    assert len(release_json["statistics"]) == 2
    assert release_json["statistics"][0]["relatedLot"] == "LOT-001"
    assert release_json["statistics"][0]["measure"] == "complainants"
    assert release_json["statistics"][1]["relatedLot"] == "LOT-002"
    assert release_json["statistics"][1]["measure"] == "complainants"
