# tests/test_opt_130_part_employlegis.py

from ted_and_doffin_to_ocds.converters.opt_130_part_employlegis import (
    parse_employment_legislation_url_part,
    merge_employment_legislation_url_part,
)


def test_parse_employment_legislation_url_part():
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Part">PART-0001</cbc:ID>
            <cac:TenderingTerms>
                <cac:EmploymentLegislationDocumentReference>
                    <cbc:ID>Empl1</cbc:ID>
                    <cac:Attachment>
                        <cac:ExternalReference>
                            <cbc:URI>http://employment-legislation.gov.stat</cbc:URI>
                        </cac:ExternalReference>
                    </cac:Attachment>
                </cac:EmploymentLegislationDocumentReference>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </root>
    """

    result = parse_employment_legislation_url_part(xml_content)

    assert result is not None
    assert "tender" in result
    assert "documents" in result["tender"]
    assert len(result["tender"]["documents"]) == 1

    doc = result["tender"]["documents"][0]
    assert doc["id"] == "Empl1"
    assert doc["url"] == "http://employment-legislation.gov.stat"


def test_merge_employment_legislation_url_part():
    release_json = {"tender": {"documents": []}}
    empl_legislation_data = {
        "tender": {
            "documents": [
                {"id": "Empl1", "url": "http://employment-legislation.gov.stat"}
            ]
        }
    }

    merge_employment_legislation_url_part(release_json, empl_legislation_data)

    assert "documents" in release_json["tender"]
    assert len(release_json["tender"]["documents"]) == 1

    doc = release_json["tender"]["documents"][0]
    assert doc["id"] == "Empl1"
    assert doc["url"] == "http://employment-legislation.gov.stat"


def test_merge_employment_legislation_url_part_existing_document():
    release_json = {
        "tender": {"documents": [{"id": "Empl1", "url": "http://old-url.com"}]}
    }
    empl_legislation_data = {
        "tender": {"documents": [{"id": "Empl1", "url": "http://new-url.com"}]}
    }

    merge_employment_legislation_url_part(release_json, empl_legislation_data)

    assert len(release_json["tender"]["documents"]) == 1

    doc = release_json["tender"]["documents"][0]
    assert doc["id"] == "Empl1"
    assert doc["url"] == "http://new-url.com"
