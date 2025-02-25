# tests/test_bt_502_organization_company.py

from src.ted_and_doffin_to_ocds.converters.eforms.bt_502_organization_company import (
    merge_organization_contact_point,
    parse_organization_contact_point,
)


def test_parse_organization_contact_point() -> None:
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
                            <cbc:Name>Press Department</cbc:Name>
                        </cac:Contact>
                    </efac:Company>
                </efac:Organization>
            </efac:Organizations>
        </efext:EformsExtension>
    </root>
    """

    result = parse_organization_contact_point(xml_content)
    assert result == {
        "parties": [{"id": "ORG-0001", "contactPoint": {"name": "Press Department"}}]
    }


def test_merge_organization_contact_point() -> None:
    release_json = {"parties": [{"id": "ORG-0001", "name": "Test Organization"}]}

    organization_contact_point_data = {
        "parties": [{"id": "ORG-0001", "contactPoint": {"name": "Press Department"}}]
    }

    merge_organization_contact_point(release_json, organization_contact_point_data)

    assert release_json == {
        "parties": [
            {
                "id": "ORG-0001",
                "name": "Test Organization",
                "contactPoint": {"name": "Press Department"},
            }
        ]
    }


def test_merge_organization_contact_point_new_party() -> None:
    release_json = {"parties": [{"id": "ORG-0001", "name": "Test Organization"}]}

    organization_contact_point_data = {
        "parties": [{"id": "ORG-0002", "contactPoint": {"name": "HR Department"}}]
    }

    merge_organization_contact_point(release_json, organization_contact_point_data)

    assert release_json == {
        "parties": [
            {"id": "ORG-0001", "name": "Test Organization"},
            {"id": "ORG-0002", "contactPoint": {"name": "HR Department"}},
        ]
    }
