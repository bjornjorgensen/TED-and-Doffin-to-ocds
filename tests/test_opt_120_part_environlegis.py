# tests/test_opt_120_part_environlegis.py

from ted_and_doffin_to_ocds.converters.opt_120_part_environlegis import (
    merge_environmental_legislation_url_part,
    parse_environmental_legislation_url_part,
)


def test_parse_environmental_legislation_url_part() -> None:
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Part">PART-0001</cbc:ID>
            <cac:TenderingTerms>
                <cac:EnvironmentalLegislationDocumentReference>
                    <cbc:ID>Env1</cbc:ID>
                    <cac:Attachment>
                        <cac:ExternalReference>
                            <cbc:URI>http://environmental-legislation.gov.stat</cbc:URI>
                        </cac:ExternalReference>
                    </cac:Attachment>
                </cac:EnvironmentalLegislationDocumentReference>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </root>
    """

    result = parse_environmental_legislation_url_part(xml_content)

    assert result is not None
    assert "tender" in result
    assert "documents" in result["tender"]
    assert len(result["tender"]["documents"]) == 1

    doc = result["tender"]["documents"][0]
    assert doc["id"] == "Env1"
    assert doc["url"] == "http://environmental-legislation.gov.stat"


def test_merge_environmental_legislation_url_part() -> None:
    release_json = {"tender": {"documents": []}}
    env_legislation_data = {
        "tender": {
            "documents": [
                {"id": "Env1", "url": "http://environmental-legislation.gov.stat"}
            ]
        }
    }

    merge_environmental_legislation_url_part(release_json, env_legislation_data)

    assert "documents" in release_json["tender"]
    assert len(release_json["tender"]["documents"]) == 1

    doc = release_json["tender"]["documents"][0]
    assert doc["id"] == "Env1"
    assert doc["url"] == "http://environmental-legislation.gov.stat"


def test_merge_environmental_legislation_url_part_existing_document() -> None:
    release_json = {
        "tender": {"documents": [{"id": "Env1", "url": "http://old-url.com"}]}
    }
    env_legislation_data = {
        "tender": {"documents": [{"id": "Env1", "url": "http://new-url.com"}]}
    }

    merge_environmental_legislation_url_part(release_json, env_legislation_data)

    assert len(release_json["tender"]["documents"]) == 1

    doc = release_json["tender"]["documents"][0]
    assert doc["id"] == "Env1"
    assert doc["url"] == "http://new-url.com"
