# tests/test_bt_16_organization_company.py

from ted_and_doffin_to_ocds.converters.bt_16_organization_company import (
    merge_organization_part_name,
    parse_organization_part_name,
)


def test_parse_organization_part_name() -> None:
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
                            <cbc:Name>Ministry of Education</cbc:Name>
                        </cac:PartyName>
                        <cac:PostalAddress>
                            <cbc:Department>Procurement Department</cbc:Department>
                        </cac:PostalAddress>
                    </efac:Company>
                </efac:Organization>
            </efac:Organizations>
        </efext:EformsExtension>
    </root>
    """

    result = parse_organization_part_name(xml_content)
    assert result == {
        "parties": [
            {"id": "ORG-0001", "name": "Ministry of Education - Procurement Department"}
        ]
    }


def test_merge_organization_part_name() -> None:
    release_json = {"parties": [{"id": "ORG-0001", "name": "Ministry of Education"}]}

    organization_part_name_data = {
        "parties": [
            {"id": "ORG-0001", "name": "Ministry of Education - Procurement Department"}
        ]
    }

    merge_organization_part_name(release_json, organization_part_name_data)

    assert release_json == {
        "parties": [
            {"id": "ORG-0001", "name": "Ministry of Education - Procurement Department"}
        ]
    }


def test_merge_organization_part_name_new_party() -> None:
    release_json = {"parties": [{"id": "ORG-0001", "name": "Ministry of Education"}]}

    organization_part_name_data = {
        "parties": [
            {"id": "ORG-0002", "name": "Ministry of Health - Research Department"}
        ]
    }

    merge_organization_part_name(release_json, organization_part_name_data)

    assert release_json == {
        "parties": [
            {"id": "ORG-0001", "name": "Ministry of Education"},
            {"id": "ORG-0002", "name": "Ministry of Health - Research Department"},
        ]
    }
