# tests/test_bt_712b_lotresult.py

import pytest
from lxml import etree

from src.ted_and_doffin_to_ocds.converters.eforms.bt_712b_lotresult import (
    merge_buyer_review_complainants_number,
    parse_buyer_review_complainants_number,
)

NAMESPACES = {
    "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
    "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    "efbc": "http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1",
}


def create_xml_content(lot_data):
    root = etree.Element("root", nsmap=NAMESPACES)
    notice_result = etree.SubElement(root, f"{{{NAMESPACES['efac']}}}NoticeResult")

    for lot_id, number in lot_data.items():
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
        stats_code.text = "complainants"
        stats_numeric = etree.SubElement(
            appeal_stats, f"{{{NAMESPACES['efbc']}}}StatisticsNumeric"
        )
        stats_numeric.text = str(number)

    return etree.tostring(root)


def test_parse_buyer_review_complainants_number() -> None:
    xml_content = create_xml_content({"LOT-001": 2, "LOT-002": 3})
    result = parse_buyer_review_complainants_number(xml_content)

    assert result is not None
    assert "statistics" in result
    assert len(result["statistics"]) == 2

    assert result["statistics"][0] == {
        "id": "1",
        "value": 2,
        "measure": "complainants",
        "scope": "complaints",
        "relatedLot": "LOT-001",
    }
    assert result["statistics"][1] == {
        "id": "2",
        "value": 3,
        "measure": "complainants",
        "scope": "complaints",
        "relatedLot": "LOT-002",
    }


def test_parse_buyer_review_complainants_number_no_data() -> None:
    xml_content = "<root></root>"
    result = parse_buyer_review_complainants_number(xml_content)
    assert result is None


def test_parse_buyer_review_complainants_number_missing_lot_id() -> None:
    xml_content = create_xml_content({"": 2})
    result = parse_buyer_review_complainants_number(xml_content)
    assert result is None


def test_merge_buyer_review_complainants_number() -> None:
    release_json = {"statistics": []}
    complainants_number_data = {
        "statistics": [
            {
                "id": "1",
                "value": 2,
                "measure": "complainants",
                "scope": "complaints",
                "relatedLot": "LOT-001",
            }
        ]
    }

    merge_buyer_review_complainants_number(release_json, complainants_number_data)

    assert len(release_json["statistics"]) == 1
    assert release_json["statistics"][0] == complainants_number_data["statistics"][0]


def test_merge_buyer_review_complainants_number_update_existing() -> None:
    release_json = {
        "statistics": [
            {
                "id": "1",
                "value": 2,
                "measure": "complainants",
                "scope": "complaints",
                "relatedLot": "LOT-001",
            }
        ]
    }
    complainants_number_data = {
        "statistics": [
            {
                "id": "2",
                "value": 3,
                "measure": "complainants",
                "scope": "complaints",
                "relatedLot": "LOT-001",
            }
        ]
    }

    merge_buyer_review_complainants_number(release_json, complainants_number_data)

    assert len(release_json["statistics"]) == 1
    assert release_json["statistics"][0]["id"] == "2"
    assert release_json["statistics"][0]["value"] == 3


def test_merge_buyer_review_complainants_number_no_data() -> None:
    release_json = {"statistics": []}
    merge_buyer_review_complainants_number(release_json, None)
    assert "statistics" in release_json
    assert len(release_json["statistics"]) == 0


@pytest.fixture
def sample_xml_content():
    return create_xml_content({"LOT-001": 2, "LOT-002": 3})


def test_integration(sample_xml_content) -> None:
    # Parse the XML content
    parsed_data = parse_buyer_review_complainants_number(sample_xml_content)
    assert parsed_data is not None

    # Create a mock release JSON
    release_json = {"statistics": []}

    # Merge the parsed data into the release JSON
    merge_buyer_review_complainants_number(release_json, parsed_data)

    # Check the final result
    assert len(release_json["statistics"]) == 2
    assert release_json["statistics"][0]["relatedLot"] == "LOT-001"
    assert release_json["statistics"][0]["value"] == 2
    assert release_json["statistics"][1]["relatedLot"] == "LOT-002"
    assert release_json["statistics"][1]["value"] == 3
