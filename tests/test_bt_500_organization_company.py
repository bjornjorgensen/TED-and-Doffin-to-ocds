# tests/test_bt_500_organization_company.py

from src.ted_and_doffin_to_ocds.converters.eforms.bt_500_organization_company import (
    merge_organization_name,
    parse_organization_name,
)


def test_parse_organization_name() -> None:
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
                        <cac:PartyName>
                            <cbc:Name languageID="ENG">Ministry of Education</cbc:Name>
                        </cac:PartyName>
                    </efac:Company>
                </efac:Organization>
            </efac:Organizations>
        </efext:EformsExtension>
    </root>
    """

    result = parse_organization_name(xml_content)
    assert result == {"parties": [{"id": "ORG-0001", "name": "Ministry of Education"}]}


def test_merge_organization_name() -> None:
    release_json = {
        "parties": [{"id": "ORG-0001", "address": {"streetAddress": "123 Main St"}}]
    }

    organization_name_data = {
        "parties": [{"id": "ORG-0001", "name": "Ministry of Education"}]
    }

    merge_organization_name(release_json, organization_name_data)

    assert release_json == {
        "parties": [
            {
                "id": "ORG-0001",
                "name": "Ministry of Education",
                "address": {"streetAddress": "123 Main St"},
            }
        ]
    }


def test_merge_organization_name_new_party() -> None:
    release_json = {"parties": [{"id": "ORG-0001", "name": "Ministry of Education"}]}

    organization_name_data = {
        "parties": [{"id": "ORG-0002", "name": "Ministry of Health"}]
    }

    merge_organization_name(release_json, organization_name_data)

    assert release_json == {
        "parties": [
            {"id": "ORG-0001", "name": "Ministry of Education"},
            {"id": "ORG-0002", "name": "Ministry of Health"},
        ]
    }
