# tests/test_opt_120_lot_environlegis.py

from ted_and_doffin_to_ocds.converters.opt_120_lot_environlegis import (
    parse_environmental_legislation_url,
    merge_environmental_legislation_url,
)


def test_parse_environmental_legislation_url():
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
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

    result = parse_environmental_legislation_url(xml_content)

    assert result is not None
    assert "tender" in result
    assert "documents" in result["tender"]
    assert len(result["tender"]["documents"]) == 1

    doc = result["tender"]["documents"][0]
    assert doc["id"] == "Env1"
    assert doc["url"] == "http://environmental-legislation.gov.stat"
    assert doc["relatedLots"] == ["LOT-0001"]


def test_merge_environmental_legislation_url():
    release_json = {"tender": {"documents": []}}
    env_legislation_data = {
        "tender": {
            "documents": [
                {
                    "id": "Env1",
                    "url": "http://environmental-legislation.gov.stat",
                    "relatedLots": ["LOT-0001"],
                }
            ]
        }
    }

    merge_environmental_legislation_url(release_json, env_legislation_data)

    assert "documents" in release_json["tender"]
    assert len(release_json["tender"]["documents"]) == 1

    doc = release_json["tender"]["documents"][0]
    assert doc["id"] == "Env1"
    assert doc["url"] == "http://environmental-legislation.gov.stat"
    assert doc["relatedLots"] == ["LOT-0001"]


def test_merge_environmental_legislation_url_existing_document():
    release_json = {
        "tender": {
            "documents": [
                {"id": "Env1", "url": "http://old-url.com", "relatedLots": ["LOT-0002"]}
            ]
        }
    }
    env_legislation_data = {
        "tender": {
            "documents": [
                {"id": "Env1", "url": "http://new-url.com", "relatedLots": ["LOT-0001"]}
            ]
        }
    }

    merge_environmental_legislation_url(release_json, env_legislation_data)

    assert len(release_json["tender"]["documents"]) == 1

    doc = release_json["tender"]["documents"][0]
    assert doc["id"] == "Env1"
    assert doc["url"] == "http://new-url.com"
    assert set(doc["relatedLots"]) == {"LOT-0001", "LOT-0002"}
