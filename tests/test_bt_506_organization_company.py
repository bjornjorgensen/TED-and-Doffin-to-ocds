# tests/test_bt_506_organization_company.py

from ted_and_doffin_to_ocds.converters.bt_506_organization_company import (
    parse_organization_email,
    merge_organization_email,
)


def test_parse_organization_email():
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
                        <cac:Contact>
                            <cbc:ElectronicMail>press@xyz.europa.eu</cbc:ElectronicMail>
                        </cac:Contact>
                    </efac:Company>
                </efac:Organization>
            </efac:Organizations>
        </efext:EformsExtension>
    </root>
    """

    result = parse_organization_email(xml_content)
    assert result == {
        "parties": [
            {"id": "ORG-0001", "contactPoint": {"email": "press@xyz.europa.eu"}}
        ]
    }


def test_merge_organization_email():
    release_json = {"parties": [{"id": "ORG-0001", "name": "Test Organization"}]}

    organization_email_data = {
        "parties": [
            {"id": "ORG-0001", "contactPoint": {"email": "press@xyz.europa.eu"}}
        ]
    }

    merge_organization_email(release_json, organization_email_data)

    assert release_json == {
        "parties": [
            {
                "id": "ORG-0001",
                "name": "Test Organization",
                "contactPoint": {"email": "press@xyz.europa.eu"},
            }
        ]
    }


def test_merge_organization_email_new_party():
    release_json = {"parties": [{"id": "ORG-0001", "name": "Test Organization"}]}

    organization_email_data = {
        "parties": [{"id": "ORG-0002", "contactPoint": {"email": "info@abc.europa.eu"}}]
    }

    merge_organization_email(release_json, organization_email_data)

    assert release_json == {
        "parties": [
            {"id": "ORG-0001", "name": "Test Organization"},
            {"id": "ORG-0002", "contactPoint": {"email": "info@abc.europa.eu"}},
        ]
    }
