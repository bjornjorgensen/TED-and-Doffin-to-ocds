# tests/test_bt_506_organization_touchpoint.py

from src.ted_and_doffin_to_ocds.converters.eforms.bt_506_organization_touchpoint import (
    merge_organization_touchpoint_email,
    parse_organization_touchpoint_email,
)


def test_parse_organization_touchpoint_email() -> None:
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
                            <cbc:ElectronicMail>abc@xyz.europa.eu</cbc:ElectronicMail>
                        </cac:Contact>
                    </efac:TouchPoint>
                </efac:Organization>
            </efac:Organizations>
        </efext:EformsExtension>
    </root>
    """

    result = parse_organization_touchpoint_email(xml_content)
    assert result == {
        "parties": [
            {
                "id": "TPO-0001",
                "contactPoint": {"email": "abc@xyz.europa.eu"},
                "identifier": {"id": "998298", "scheme": "internal"},
            }
        ]
    }


def test_merge_organization_touchpoint_email() -> None:
    release_json = {"parties": [{"id": "TPO-0001", "name": "Test Organization"}]}

    organization_touchpoint_email_data = {
        "parties": [
            {
                "id": "TPO-0001",
                "contactPoint": {"email": "abc@xyz.europa.eu"},
                "identifier": {"id": "998298", "scheme": "internal"},
            }
        ]
    }

    merge_organization_touchpoint_email(
        release_json, organization_touchpoint_email_data
    )

    assert release_json == {
        "parties": [
            {
                "id": "TPO-0001",
                "name": "Test Organization",
                "contactPoint": {"email": "abc@xyz.europa.eu"},
                "identifier": {"id": "998298", "scheme": "internal"},
            }
        ]
    }


def test_merge_organization_touchpoint_email_new_party() -> None:
    release_json = {"parties": [{"id": "TPO-0001", "name": "Test Organization"}]}

    organization_touchpoint_email_data = {
        "parties": [
            {
                "id": "TPO-0002",
                "contactPoint": {"email": "info@abc.europa.eu"},
                "identifier": {"id": "998299", "scheme": "internal"},
            }
        ]
    }

    merge_organization_touchpoint_email(
        release_json, organization_touchpoint_email_data
    )

    assert release_json == {
        "parties": [
            {"id": "TPO-0001", "name": "Test Organization"},
            {
                "id": "TPO-0002",
                "contactPoint": {"email": "info@abc.europa.eu"},
                "identifier": {"id": "998299", "scheme": "internal"},
            },
        ]
    }
