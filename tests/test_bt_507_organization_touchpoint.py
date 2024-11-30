# tests/test_bt_507_organization_touchpoint.py

from ted_and_doffin_to_ocds.converters.bt_507_organization_touchpoint import (
    merge_organization_touchpoint_country_subdivision,
    parse_organization_touchpoint_country_subdivision,
)


def test_parse_organization_touchpoint_country_subdivision() -> None:
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
                        <cac:PostalAddress>
                            <cbc:CountrySubentityCode listName="nuts-lvl3">XY374</cbc:CountrySubentityCode>
                        </cac:PostalAddress>
                    </efac:TouchPoint>
                </efac:Organization>
            </efac:Organizations>
        </efext:EformsExtension>
    </root>
    """

    result = parse_organization_touchpoint_country_subdivision(xml_content)
    assert result == {
        "parties": [
            {
                "id": "TPO-0001",
                "address": {"region": "XY374"},
                "identifier": {"id": "998298", "scheme": "internal"},
            }
        ]
    }


def test_merge_organization_touchpoint_country_subdivision() -> None:
    release_json = {"parties": [{"id": "TPO-0001", "name": "Test Organization"}]}

    organization_touchpoint_country_subdivision_data = {
        "parties": [
            {
                "id": "TPO-0001",
                "address": {"region": "XY374"},
                "identifier": {"id": "998298", "scheme": "internal"},
            }
        ]
    }

    merge_organization_touchpoint_country_subdivision(
        release_json, organization_touchpoint_country_subdivision_data
    )

    assert release_json == {
        "parties": [
            {
                "id": "TPO-0001",
                "name": "Test Organization",
                "address": {"region": "XY374"},
                "identifier": {"id": "998298", "scheme": "internal"},
            }
        ]
    }


def test_merge_organization_touchpoint_country_subdivision_new_party() -> None:
    release_json = {"parties": [{"id": "TPO-0001", "name": "Test Organization"}]}

    organization_touchpoint_country_subdivision_data = {
        "parties": [
            {
                "id": "TPO-0002",
                "address": {"region": "ZZ999"},
                "identifier": {"id": "998299", "scheme": "internal"},
            }
        ]
    }

    merge_organization_touchpoint_country_subdivision(
        release_json, organization_touchpoint_country_subdivision_data
    )

    assert release_json == {
        "parties": [
            {"id": "TPO-0001", "name": "Test Organization"},
            {
                "id": "TPO-0002",
                "address": {"region": "ZZ999"},
                "identifier": {"id": "998299", "scheme": "internal"},
            },
        ]
    }
