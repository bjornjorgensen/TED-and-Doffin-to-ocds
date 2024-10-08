# tests/test_bt_500_ubo.py

from ted_and_doffin_to_ocds.converters.bt_500_ubo import parse_ubo_name, merge_ubo_name


def test_parse_ubo_name():
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
                    </efac:Company>
                </efac:Organization>
                <efac:UltimateBeneficialOwner>
                    <cbc:ID schemeName="ubo">UBO-0001</cbc:ID>
                    <cbc:FamilyName>Mouse</cbc:FamilyName>
                </efac:UltimateBeneficialOwner>
            </efac:Organizations>
        </efext:EformsExtension>
    </root>
    """

    result = parse_ubo_name(xml_content)
    assert result == {
        "parties": [
            {
                "id": "ORG-0001",
                "beneficialOwners": [{"id": "UBO-0001", "name": "Mouse"}],
            }
        ]
    }


def test_merge_ubo_name():
    release_json = {"parties": [{"id": "ORG-0001", "name": "Test Organization"}]}

    ubo_name_data = {
        "parties": [
            {
                "id": "ORG-0001",
                "beneficialOwners": [{"id": "UBO-0001", "name": "Mouse"}],
            }
        ]
    }

    merge_ubo_name(release_json, ubo_name_data)

    assert release_json == {
        "parties": [
            {
                "id": "ORG-0001",
                "name": "Test Organization",
                "beneficialOwners": [{"id": "UBO-0001", "name": "Mouse"}],
            }
        ]
    }


def test_merge_ubo_name_new_party():
    release_json = {"parties": [{"id": "ORG-0001", "name": "Test Organization"}]}

    ubo_name_data = {
        "parties": [
            {"id": "ORG-0002", "beneficialOwners": [{"id": "UBO-0002", "name": "Duck"}]}
        ]
    }

    merge_ubo_name(release_json, ubo_name_data)

    assert release_json == {
        "parties": [
            {"id": "ORG-0001", "name": "Test Organization"},
            {
                "id": "ORG-0002",
                "beneficialOwners": [{"id": "UBO-0002", "name": "Duck"}],
            },
        ]
    }
