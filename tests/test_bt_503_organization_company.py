# tests/test_bt_503_organization_company.py

from ted_and_doffin_to_ocds.converters.bt_503_organization_company import (
    merge_organization_telephone,
    parse_organization_telephone,
)


def test_parse_organization_telephone() -> None:
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
                            <cbc:Telephone>+123 45678</cbc:Telephone>
                        </cac:Contact>
                    </efac:Company>
                </efac:Organization>
            </efac:Organizations>
        </efext:EformsExtension>
    </root>
    """

    result = parse_organization_telephone(xml_content)
    assert result == {
        "parties": [{"id": "ORG-0001", "contactPoint": {"telephone": "+123 45678"}}]
    }


def test_merge_organization_telephone() -> None:
    release_json = {"parties": [{"id": "ORG-0001", "name": "Test Organization"}]}

    organization_telephone_data = {
        "parties": [{"id": "ORG-0001", "contactPoint": {"telephone": "+123 45678"}}]
    }

    merge_organization_telephone(release_json, organization_telephone_data)

    assert release_json == {
        "parties": [
            {
                "id": "ORG-0001",
                "name": "Test Organization",
                "contactPoint": {"telephone": "+123 45678"},
            }
        ]
    }


def test_merge_organization_telephone_new_party() -> None:
    release_json = {"parties": [{"id": "ORG-0001", "name": "Test Organization"}]}

    organization_telephone_data = {
        "parties": [{"id": "ORG-0002", "contactPoint": {"telephone": "+987 65432"}}]
    }

    merge_organization_telephone(release_json, organization_telephone_data)

    assert release_json == {
        "parties": [
            {"id": "ORG-0001", "name": "Test Organization"},
            {"id": "ORG-0002", "contactPoint": {"telephone": "+987 65432"}},
        ]
    }
