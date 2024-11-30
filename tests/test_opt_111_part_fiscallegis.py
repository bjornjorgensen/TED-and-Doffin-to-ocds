# tests/test_opt_111_part_fiscallegis.py

import pytest

from ted_and_doffin_to_ocds.converters.opt_111_part_fiscallegis import (
    merge_part_fiscal_legislation_document_id,
    parse_part_fiscal_legislation_document_id,
)


@pytest.fixture
def sample_xml() -> str:
    return """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Part">PART-0001</cbc:ID>
            <cac:TenderingTerms>
                <cac:FiscalLegislationDocumentReference>
                    <cbc:ID>Fiscal1</cbc:ID>
                    <cac:Attachment>
                        <cac:ExternalReference>
                            <cbc:URI>https://fiscal-legislation.gov.stat</cbc:URI>
                        </cac:ExternalReference>
                    </cac:Attachment>
                </cac:FiscalLegislationDocumentReference>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </root>
    """


def test_parse_part_fiscal_legislation_document_id(sample_xml) -> None:
    result = parse_part_fiscal_legislation_document_id(sample_xml)
    assert result is not None
    assert "tender" in result
    assert "documents" in result["tender"]
    assert len(result["tender"]["documents"]) == 1
    assert result["tender"]["documents"][0]["id"] == "Fiscal1"
    assert result["tender"]["documents"][0]["documentType"] == "legislation"


def test_merge_part_fiscal_legislation_document_id() -> None:
    fiscal_legislation_data = {
        "tender": {"documents": [{"id": "Fiscal1", "documentType": "legislation"}]}
    }
    release_json = {}
    merge_part_fiscal_legislation_document_id(release_json, fiscal_legislation_data)
    assert "tender" in release_json
    assert "documents" in release_json["tender"]
    assert len(release_json["tender"]["documents"]) == 1
    assert release_json["tender"]["documents"][0]["id"] == "Fiscal1"
    assert release_json["tender"]["documents"][0]["documentType"] == "legislation"


def test_merge_part_fiscal_legislation_document_id_existing_document() -> None:
    fiscal_legislation_data = {
        "tender": {"documents": [{"id": "Fiscal1", "documentType": "legislation"}]}
    }
    release_json = {
        "tender": {"documents": [{"id": "Fiscal1", "documentType": "otherType"}]}
    }
    merge_part_fiscal_legislation_document_id(release_json, fiscal_legislation_data)
    assert len(release_json["tender"]["documents"]) == 1
    assert release_json["tender"]["documents"][0]["id"] == "Fiscal1"
    assert release_json["tender"]["documents"][0]["documentType"] == "legislation"


def test_parse_part_fiscal_legislation_document_id_no_data() -> None:
    xml_content = "<root></root>"
    result = parse_part_fiscal_legislation_document_id(xml_content)
    assert result is None


def test_merge_part_fiscal_legislation_document_id_no_data() -> None:
    release_json = {}
    merge_part_fiscal_legislation_document_id(release_json, None)
    assert release_json == {}
