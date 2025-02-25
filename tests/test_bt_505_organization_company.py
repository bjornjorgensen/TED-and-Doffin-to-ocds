# tests/test_bt_505_organization_company.py

from src.ted_and_doffin_to_ocds.converters.eforms.bt_505_organization_company import (
    merge_organization_website,
    parse_organization_website,
)


def test_parse_organization_website() -> None:
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
                        <cbc:WebsiteURI>http://xyz.europa.eu/</cbc:WebsiteURI>
                    </efac:Company>
                </efac:Organization>
            </efac:Organizations>
        </efext:EformsExtension>
    </root>
    """

    result = parse_organization_website(xml_content)
    assert result == {
        "parties": [{"id": "ORG-0001", "details": {"url": "http://xyz.europa.eu/"}}]
    }


def test_merge_organization_website() -> None:
    release_json = {"parties": [{"id": "ORG-0001", "name": "Test Organization"}]}

    organization_website_data = {
        "parties": [{"id": "ORG-0001", "details": {"url": "http://xyz.europa.eu/"}}]
    }

    merge_organization_website(release_json, organization_website_data)

    assert release_json == {
        "parties": [
            {
                "id": "ORG-0001",
                "name": "Test Organization",
                "details": {"url": "http://xyz.europa.eu/"},
            }
        ]
    }


def test_merge_organization_website_new_party() -> None:
    release_json = {"parties": [{"id": "ORG-0001", "name": "Test Organization"}]}

    organization_website_data = {
        "parties": [{"id": "ORG-0002", "details": {"url": "http://abc.europa.eu/"}}]
    }

    merge_organization_website(release_json, organization_website_data)

    assert release_json == {
        "parties": [
            {"id": "ORG-0001", "name": "Test Organization"},
            {"id": "ORG-0002", "details": {"url": "http://abc.europa.eu/"}},
        ]
    }
