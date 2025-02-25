# tests/test_bt_513_organization_company.py

from src.ted_and_doffin_to_ocds.converters.eforms.bt_513_organization_company import (
    merge_organization_city,
    parse_organization_city,
)


def test_parse_organization_city() -> None:
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
                        <cac:PostalAddress>
                            <cbc:CityName>SmallCity</cbc:CityName>
                        </cac:PostalAddress>
                    </efac:Company>
                </efac:Organization>
            </efac:Organizations>
        </efext:EformsExtension>
    </root>
    """

    result = parse_organization_city(xml_content)
    assert result == {
        "parties": [{"id": "ORG-0001", "address": {"locality": "SmallCity"}}]
    }


def test_merge_organization_city() -> None:
    release_json = {"parties": [{"id": "ORG-0001", "name": "Test Organization"}]}

    organization_city_data = {
        "parties": [{"id": "ORG-0001", "address": {"locality": "SmallCity"}}]
    }

    merge_organization_city(release_json, organization_city_data)

    assert release_json == {
        "parties": [
            {
                "id": "ORG-0001",
                "name": "Test Organization",
                "address": {"locality": "SmallCity"},
            }
        ]
    }


def test_merge_organization_city_new_party() -> None:
    release_json = {"parties": [{"id": "ORG-0001", "name": "Test Organization"}]}

    organization_city_data = {
        "parties": [{"id": "ORG-0002", "address": {"locality": "BigCity"}}]
    }

    merge_organization_city(release_json, organization_city_data)

    assert release_json == {
        "parties": [
            {"id": "ORG-0001", "name": "Test Organization"},
            {"id": "ORG-0002", "address": {"locality": "BigCity"}},
        ]
    }
