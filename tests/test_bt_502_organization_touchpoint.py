# tests/test_bt_502_organization_touchpoint.py

from src.ted_and_doffin_to_ocds.converters.eforms.bt_502_organization_touchpoint import (
    merge_touchpoint_contact_point,
    parse_touchpoint_contact_point,
)


def test_parse_organization_touchpoint_contact_point() -> None:
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
                        <cac:Contact>
                            <cbc:Name>Head of Legal Department</cbc:Name>
                        </cac:Contact>
                    </efac:TouchPoint>
                </efac:Organization>
            </efac:Organizations>
        </efext:EformsExtension>
    </root>
    """

    result = parse_touchpoint_contact_point(xml_content)
    assert result == {
        "parties": [
            {
                "id": "TPO-0001",
                "contactPoint": {"name": "Head of Legal Department"},
                "identifier": {"id": "998298", "scheme": "internal"},
            }
        ]
    }


def test_merge_organization_touchpoint_contact_point() -> None:
    release_json = {"parties": [{"id": "TPO-0001", "name": "Test Organization"}]}

    organization_touchpoint_contact_point_data = {
        "parties": [
            {
                "id": "TPO-0001",
                "contactPoint": {"name": "Head of Legal Department"},
                "identifier": {"id": "998298", "scheme": "internal"},
            }
        ]
    }

    merge_touchpoint_contact_point(
        release_json, organization_touchpoint_contact_point_data
    )

    assert release_json == {
        "parties": [
            {
                "id": "TPO-0001",
                "name": "Test Organization",
                "contactPoint": {"name": "Head of Legal Department"},
                "identifier": {"id": "998298", "scheme": "internal"},
            }
        ]
    }


def test_merge_organization_touchpoint_contact_point_new_party() -> None:
    release_json = {"parties": [{"id": "TPO-0001", "name": "Test Organization"}]}

    organization_touchpoint_contact_point_data = {
        "parties": [
            {
                "id": "TPO-0002",
                "contactPoint": {"name": "Head of HR Department"},
                "identifier": {"id": "998299", "scheme": "internal"},
            }
        ]
    }

    merge_touchpoint_contact_point(
        release_json, organization_touchpoint_contact_point_data
    )

    assert release_json == {
        "parties": [
            {"id": "TPO-0001", "name": "Test Organization"},
            {
                "id": "TPO-0002",
                "contactPoint": {"name": "Head of HR Department"},
                "identifier": {"id": "998299", "scheme": "internal"},
            },
        ]
    }
