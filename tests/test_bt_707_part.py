# tests/test_bt_707_part.py
import logging

import pytest
from lxml import etree

from ted_and_doffin_to_ocds.converters.bt_707_part import (
    merge_part_documents_restricted_justification,
    parse_part_documents_restricted_justification,
)

TEST_XML = """<?xml version="1.0" encoding="UTF-8"?>
<ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
                   xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
                   xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
    <cac:ProcurementProjectLot>
        <cbc:ID schemeName="Part">PART-0001</cbc:ID>
        <cac:TenderingTerms>
            <cac:CallForTendersDocumentReference>
                <cbc:ID>20210521/CTFD/ENG/7654-02</cbc:ID>
                <cbc:DocumentTypeCode listName="communication-justification">ipr-iss</cbc:DocumentTypeCode>
            </cac:CallForTendersDocumentReference>
        </cac:TenderingTerms>
    </cac:ProcurementProjectLot>
</ContractAwardNotice>"""

INVALID_XML = "<?xml version='1.0'?><invalid>"


@pytest.fixture
def caplog(caplog):
    caplog.set_level(logging.INFO)
    return caplog


def test_parse_part_documents_restricted_justification_success() -> None:
    """Test successful parsing of document justification."""
    result = parse_part_documents_restricted_justification(TEST_XML)

    assert result is not None
    assert "tender" in result
    assert "documents" in result["tender"]
    assert len(result["tender"]["documents"]) == 1

    document = result["tender"]["documents"][0]
    assert document["id"] == "20210521/CTFD/ENG/7654-02"
    assert document["accessDetails"] == "Intellectual property right issues"


def test_parse_part_documents_restricted_justification_invalid_xml(caplog) -> None:
    """Test handling of invalid XML."""
    with pytest.raises(etree.XMLSyntaxError):
        parse_part_documents_restricted_justification(INVALID_XML)
    assert "Failed to parse XML content" in caplog.text


def test_merge_part_documents_restricted_justification() -> None:
    """Test merging document justification into release JSON."""
    release_json = {"tender": {"documents": []}}
    part_documents_data = {
        "tender": {
            "documents": [
                {
                    "id": "20210521/CTFD/ENG/7654-02",
                    "accessDetails": "Restricted. Intellectual property rights issues",
                }
            ]
        }
    }

    merge_part_documents_restricted_justification(release_json, part_documents_data)

    assert len(release_json["tender"]["documents"]) == 1
    assert release_json["tender"]["documents"][0]["id"] == "20210521/CTFD/ENG/7654-02"
    assert (
        release_json["tender"]["documents"][0]["accessDetails"]
        == "Restricted. Intellectual property rights issues"
    )


def test_merge_part_documents_restricted_justification_empty(caplog) -> None:
    """Test merging with empty data."""
    release_json = {"tender": {"documents": []}}
    merge_part_documents_restricted_justification(release_json, None)
    assert "No part documents restricted justification data to merge" in caplog.text


def test_merge_part_documents_restricted_justification_existing() -> None:
    """Test merging when document already exists."""
    release_json = {
        "tender": {
            "documents": [
                {
                    "id": "20210521/CTFD/ENG/7654-02",
                    "accessDetails": "Old justification",
                }
            ]
        }
    }
    part_documents_data = {
        "tender": {
            "documents": [
                {
                    "id": "20210521/CTFD/ENG/7654-02",
                    "accessDetails": "Restricted. Intellectual property rights issues",
                }
            ]
        }
    }

    merge_part_documents_restricted_justification(release_json, part_documents_data)

    assert len(release_json["tender"]["documents"]) == 1
    assert (
        release_json["tender"]["documents"][0]["accessDetails"]
        == "Restricted. Intellectual property rights issues"
    )


if __name__ == "__main__":
    pytest.main(["-v", "-s"])
