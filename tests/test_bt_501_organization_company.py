# tests/test_bt_501_organization_company.py

from src.ted_and_doffin_to_ocds.converters.eforms.bt_501_organization_company import (
    merge_organization_identifier,
    parse_organization_identifier,
)


def test_parse_organization_identifier() -> None:
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
          xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1">
        <efext:EformsExtension>
            <efac:Organizations>
                <efac:Organization>
                    <efac:Company>
                        <cac:PartyIdentification>
                            <cbc:ID schemeName="organization">ORG-0001</cbc:ID>
                        </cac:PartyIdentification>
                        <cac:PartyLegalEntity>
                            <cbc:CompanyID>09506232</cbc:CompanyID>
                        </cac:PartyLegalEntity>
                    </efac:Company>
                </efac:Organization>
            </efac:Organizations>
        </efext:EformsExtension>
    </root>
    """

    result = parse_organization_identifier(xml_content)
    assert result == {
        "parties": [
            {
                "id": "ORG-0001",
                "additionalIdentifiers": [{"id": "09506232", "scheme": "GB-COH"}],
            }
        ]
    }


def test_merge_organization_identifier() -> None:
    release_json = {"parties": [{"id": "ORG-0001", "name": "Test Organization"}]}

    organization_identifier_data = {
        "parties": [
            {
                "id": "ORG-0001",
                "additionalIdentifiers": [{"id": "09506232", "scheme": "GB-COH"}],
            }
        ]
    }

    merge_organization_identifier(release_json, organization_identifier_data)

    assert release_json == {
        "parties": [
            {
                "id": "ORG-0001",
                "name": "Test Organization",
                "additionalIdentifiers": [{"id": "09506232", "scheme": "GB-COH"}],
            }
        ]
    }


def test_merge_organization_identifier_new_party() -> None:
    release_json = {"parties": [{"id": "ORG-0001", "name": "Test Organization"}]}

    organization_identifier_data = {
        "parties": [
            {
                "id": "ORG-0002",
                "additionalIdentifiers": [{"id": "12345678", "scheme": "GB-COH"}],
            }
        ]
    }

    merge_organization_identifier(release_json, organization_identifier_data)

    assert release_json == {
        "parties": [
            {"id": "ORG-0001", "name": "Test Organization"},
            {
                "id": "ORG-0002",
                "additionalIdentifiers": [{"id": "12345678", "scheme": "GB-COH"}],
            },
        ]
    }
