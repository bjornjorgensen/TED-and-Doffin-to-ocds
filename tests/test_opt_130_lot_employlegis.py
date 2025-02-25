# tests/test_opt_130_lot_employlegis.py

from src.ted_and_doffin_to_ocds.converters.eforms.opt_130_lot_employlegis import (
    merge_employment_legislation_url,
    parse_employment_legislation_url,
)


def test_parse_employment_legislation_url() -> None:
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
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

    result = parse_employment_legislation_url(xml_content)

    assert result is not None
    assert "tender" in result
    assert "documents" in result["tender"]
    assert len(result["tender"]["documents"]) == 1

    doc = result["tender"]["documents"][0]
    assert doc["id"] == "Empl1"
    assert doc["url"] == "http://employment-legislation.gov.stat"
    assert doc["relatedLots"] == ["LOT-0001"]


def test_merge_employment_legislation_url() -> None:
    release_json = {"tender": {"documents": []}}
    empl_legislation_data = {
        "tender": {
            "documents": [
                {
                    "id": "Empl1",
                    "url": "http://employment-legislation.gov.stat",
                    "relatedLots": ["LOT-0001"],
                }
            ]
        }
    }

    merge_employment_legislation_url(release_json, empl_legislation_data)

    assert "documents" in release_json["tender"]
    assert len(release_json["tender"]["documents"]) == 1

    doc = release_json["tender"]["documents"][0]
    assert doc["id"] == "Empl1"
    assert doc["url"] == "http://employment-legislation.gov.stat"
    assert doc["relatedLots"] == ["LOT-0001"]


def test_merge_employment_legislation_url_existing_document() -> None:
    release_json = {
        "tender": {
            "documents": [
                {
                    "id": "Empl1",
                    "url": "http://old-url.com",
                    "relatedLots": ["LOT-0002"],
                }
            ]
        }
    }
    empl_legislation_data = {
        "tender": {
            "documents": [
                {
                    "id": "Empl1",
                    "url": "http://new-url.com",
                    "relatedLots": ["LOT-0001"],
                }
            ]
        }
    }

    merge_employment_legislation_url(release_json, empl_legislation_data)

    assert len(release_json["tender"]["documents"]) == 1

    doc = release_json["tender"]["documents"][0]
    assert doc["id"] == "Empl1"
    assert doc["url"] == "http://new-url.com"
    assert set(doc["relatedLots"]) == {"LOT-0001", "LOT-0002"}
