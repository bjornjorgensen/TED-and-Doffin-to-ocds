# tests/test_opt_112_part_environlegis.py

import pytest
from ted_and_doffin_to_ocds.converters.opt_112_part_environlegis import (
    parse_part_environmental_legislation_document_id,
    merge_part_environmental_legislation_document_id,
)


@pytest.fixture
def sample_xml():
    return """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Part">PART-0001</cbc:ID>
            <cac:TenderingTerms>
                <cac:EnvironmentalLegislationDocumentReference>
                    <cbc:ID>Env1</cbc:ID>
                </cac:EnvironmentalLegislationDocumentReference>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </root>
    """


def test_parse_part_environmental_legislation_document_id(sample_xml):
    result = parse_part_environmental_legislation_document_id(sample_xml)
    assert result is not None
    assert "tender" in result
    assert "documents" in result["tender"]
    assert len(result["tender"]["documents"]) == 1
    assert result["tender"]["documents"][0]["id"] == "Env1"
    assert result["tender"]["documents"][0]["documentType"] == "legislation"


def test_merge_part_environmental_legislation_document_id():
    environmental_legislation_data = {
        "tender": {"documents": [{"id": "Env1", "documentType": "legislation"}]}
    }
    release_json = {}
    merge_part_environmental_legislation_document_id(
        release_json, environmental_legislation_data
    )
    assert "tender" in release_json
    assert "documents" in release_json["tender"]
    assert len(release_json["tender"]["documents"]) == 1
    assert release_json["tender"]["documents"][0]["id"] == "Env1"
    assert release_json["tender"]["documents"][0]["documentType"] == "legislation"


def test_merge_part_environmental_legislation_document_id_existing_document():
    environmental_legislation_data = {
        "tender": {"documents": [{"id": "Env1", "documentType": "legislation"}]}
    }
    release_json = {
        "tender": {"documents": [{"id": "Env1", "documentType": "otherType"}]}
    }
    merge_part_environmental_legislation_document_id(
        release_json, environmental_legislation_data
    )
    assert len(release_json["tender"]["documents"]) == 1
    assert release_json["tender"]["documents"][0]["id"] == "Env1"
    assert release_json["tender"]["documents"][0]["documentType"] == "legislation"


def test_parse_part_environmental_legislation_document_id_no_data():
    xml_content = "<root></root>"
    result = parse_part_environmental_legislation_document_id(xml_content)
    assert result is None


def test_merge_part_environmental_legislation_document_id_no_data():
    release_json = {}
    merge_part_environmental_legislation_document_id(release_json, None)
    assert release_json == {}