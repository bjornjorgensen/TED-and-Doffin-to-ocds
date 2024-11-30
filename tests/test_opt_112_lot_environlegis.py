# tests/test_opt_112_lot_environlegis.py

import pytest

from ted_and_doffin_to_ocds.converters.opt_112_lot_environlegis import (
    merge_environmental_legislation_document_id,
    parse_environmental_legislation_document_id,
)


@pytest.fixture
def sample_xml() -> str:
    return """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:TenderingTerms>
                <cac:EnvironmentalLegislationDocumentReference>
                    <cbc:ID>Env1</cbc:ID>
                </cac:EnvironmentalLegislationDocumentReference>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </root>
    """


def test_parse_environmental_legislation_document_id(sample_xml) -> None:
    result = parse_environmental_legislation_document_id(sample_xml)
    assert result is not None
    assert "tender" in result
    assert "documents" in result["tender"]
    assert len(result["tender"]["documents"]) == 1
    assert result["tender"]["documents"][0]["id"] == "Env1"
    assert result["tender"]["documents"][0]["documentType"] == "legislation"
    assert result["tender"]["documents"][0]["relatedLots"] == ["LOT-0001"]


def test_merge_environmental_legislation_document_id() -> None:
    environmental_legislation_data = {
        "tender": {
            "documents": [
                {
                    "id": "Env1",
                    "documentType": "legislation",
                    "relatedLots": ["LOT-0001"],
                }
            ]
        }
    }
    release_json = {}
    merge_environmental_legislation_document_id(
        release_json, environmental_legislation_data
    )
    assert "tender" in release_json
    assert "documents" in release_json["tender"]
    assert len(release_json["tender"]["documents"]) == 1
    assert release_json["tender"]["documents"][0]["id"] == "Env1"
    assert release_json["tender"]["documents"][0]["documentType"] == "legislation"
    assert release_json["tender"]["documents"][0]["relatedLots"] == ["LOT-0001"]


def test_merge_environmental_legislation_document_id_existing_document() -> None:
    environmental_legislation_data = {
        "tender": {
            "documents": [
                {
                    "id": "Env1",
                    "documentType": "legislation",
                    "relatedLots": ["LOT-0002"],
                }
            ]
        }
    }
    release_json = {
        "tender": {
            "documents": [
                {"id": "Env1", "documentType": "otherType", "relatedLots": ["LOT-0001"]}
            ]
        }
    }
    merge_environmental_legislation_document_id(
        release_json, environmental_legislation_data
    )
    assert len(release_json["tender"]["documents"]) == 1
    assert release_json["tender"]["documents"][0]["id"] == "Env1"
    assert release_json["tender"]["documents"][0]["documentType"] == "legislation"
    assert set(release_json["tender"]["documents"][0]["relatedLots"]) == {
        "LOT-0001",
        "LOT-0002",
    }


def test_parse_environmental_legislation_document_id_no_data() -> None:
    xml_content = "<root></root>"
    result = parse_environmental_legislation_document_id(xml_content)
    assert result is None


def test_merge_environmental_legislation_document_id_no_data() -> None:
    release_json = {}
    merge_environmental_legislation_document_id(release_json, None)
    assert release_json == {}
