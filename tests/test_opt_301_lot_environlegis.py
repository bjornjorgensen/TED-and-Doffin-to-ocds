# tests/test_opt_301_lot_environlegis.py

from ted_and_doffin_to_ocds.converters.opt_301_lot_environlegis import (
    merge_environmental_legislation_org,
    parse_environmental_legislation_org,
)


def test_parse_environmental_legislation_org() -> None:
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
          xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:TenderingTerms>
                <cac:EnvironmentalLegislationDocumentReference>
                    <cbc:ID>Env1</cbc:ID>
                    <cac:IssuerParty>
                        <cac:PartyIdentification>
                            <cbc:ID schemeName="organization">ORG-0001</cbc:ID>
                        </cac:PartyIdentification>
                    </cac:IssuerParty>
                </cac:EnvironmentalLegislationDocumentReference>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </root>
    """

    result = parse_environmental_legislation_org(xml_content)

    assert result is not None
    assert "parties" in result
    assert "tender" in result and "documents" in result["tender"]  # noqa: PT018
    assert len(result["parties"]) == 1
    assert len(result["tender"]["documents"]) == 1

    party = result["parties"][0]
    assert party["id"] == "ORG-0001"
    assert party["roles"] == ["informationService"]

    doc = result["tender"]["documents"][0]
    assert doc["id"] == "Env1"
    assert doc["publisher"]["id"] == "ORG-0001"
    assert doc["relatedLots"] == ["LOT-0001"]


def test_merge_environmental_legislation_org() -> None:
    release_json = {"parties": [], "tender": {"documents": []}}
    environ_legis_data = {
        "parties": [{"id": "ORG-0001", "roles": ["informationService"]}],
        "tender": {
            "documents": [
                {
                    "id": "Env1",
                    "publisher": {"id": "ORG-0001"},
                    "relatedLots": ["LOT-0001"],
                }
            ]
        },
    }

    merge_environmental_legislation_org(release_json, environ_legis_data)

    assert len(release_json["parties"]) == 1
    assert len(release_json["tender"]["documents"]) == 1

    party = release_json["parties"][0]
    assert party["id"] == "ORG-0001"
    assert party["roles"] == ["informationService"]

    doc = release_json["tender"]["documents"][0]
    assert doc["id"] == "Env1"
    assert doc["publisher"]["id"] == "ORG-0001"
    assert doc["relatedLots"] == ["LOT-0001"]


def test_merge_environmental_legislation_org_existing_data() -> None:
    release_json = {
        "parties": [
            {"id": "ORG-0001", "name": "Existing Organization", "roles": ["buyer"]}
        ],
        "tender": {
            "documents": [
                {
                    "id": "Env1",
                    "title": "Existing Document",
                    "relatedLots": ["LOT-0002"],
                }
            ]
        },
    }
    environ_legis_data = {
        "parties": [{"id": "ORG-0001", "roles": ["informationService"]}],
        "tender": {
            "documents": [
                {
                    "id": "Env1",
                    "publisher": {"id": "ORG-0001"},
                    "relatedLots": ["LOT-0001"],
                }
            ]
        },
    }

    merge_environmental_legislation_org(release_json, environ_legis_data)

    assert len(release_json["parties"]) == 1
    assert len(release_json["tender"]["documents"]) == 1

    party = release_json["parties"][0]
    assert party["id"] == "ORG-0001"
    assert party["name"] == "Existing Organization"
    assert set(party["roles"]) == {"buyer", "informationService"}

    doc = release_json["tender"]["documents"][0]
    assert doc["id"] == "Env1"
    assert doc["title"] == "Existing Document"
    assert doc["publisher"]["id"] == "ORG-0001"
    assert set(doc["relatedLots"]) == {"LOT-0001", "LOT-0002"}
