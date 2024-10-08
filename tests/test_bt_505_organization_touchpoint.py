# tests/test_bt_505_organization_touchpoint.py

from ted_and_doffin_to_ocds.converters.bt_505_organization_touchpoint import (
    parse_organization_touchpoint_website,
    merge_organization_touchpoint_website,
)


def test_parse_organization_touchpoint_website():
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
                        <cac:PartyLegalEntity>
                            <cbc:CompanyID>998298</cbc:CompanyID>
                        </cac:PartyLegalEntity>
                    </efac:Company>
                    <efac:TouchPoint>
                        <cac:PartyIdentification>
                            <cbc:ID schemeName="touchpoint">TPO-0001</cbc:ID>
                        </cac:PartyIdentification>
                        <cbc:WebsiteURI>http://abc.europa.eu/</cbc:WebsiteURI>
                    </efac:TouchPoint>
                </efac:Organization>
            </efac:Organizations>
        </efext:EformsExtension>
    </root>
    """

    result = parse_organization_touchpoint_website(xml_content)
    assert result == {
        "parties": [
            {
                "id": "TPO-0001",
                "details": {"url": "http://abc.europa.eu/"},
                "identifier": {"id": "998298", "scheme": "internal"},
            }
        ]
    }


def test_merge_organization_touchpoint_website():
    release_json = {"parties": [{"id": "TPO-0001", "name": "Test Organization"}]}

    organization_touchpoint_website_data = {
        "parties": [
            {
                "id": "TPO-0001",
                "details": {"url": "http://abc.europa.eu/"},
                "identifier": {"id": "998298", "scheme": "internal"},
            }
        ]
    }

    merge_organization_touchpoint_website(
        release_json, organization_touchpoint_website_data
    )

    assert release_json == {
        "parties": [
            {
                "id": "TPO-0001",
                "name": "Test Organization",
                "details": {"url": "http://abc.europa.eu/"},
                "identifier": {"id": "998298", "scheme": "internal"},
            }
        ]
    }


def test_merge_organization_touchpoint_website_new_party():
    release_json = {"parties": [{"id": "TPO-0001", "name": "Test Organization"}]}

    organization_touchpoint_website_data = {
        "parties": [
            {
                "id": "TPO-0002",
                "details": {"url": "http://xyz.europa.eu/"},
                "identifier": {"id": "998299", "scheme": "internal"},
            }
        ]
    }

    merge_organization_touchpoint_website(
        release_json, organization_touchpoint_website_data
    )

    assert release_json == {
        "parties": [
            {"id": "TPO-0001", "name": "Test Organization"},
            {
                "id": "TPO-0002",
                "details": {"url": "http://xyz.europa.eu/"},
                "identifier": {"id": "998299", "scheme": "internal"},
            },
        ]
    }
