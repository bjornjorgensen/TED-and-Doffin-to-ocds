# tests/test_bt_503_ubo.py

from src.ted_and_doffin_to_ocds.converters.eforms.bt_503_ubo import (
    merge_ubo_telephone,
    parse_ubo_telephone,
)


def test_parse_ubo_telephone() -> None:
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
                    <cbc:Telephone>+123 4567890</cbc:Telephone>
                </efac:UltimateBeneficialOwner>
            </efac:Organizations>
        </efext:EformsExtension>
    </root>
    """

    result = parse_ubo_telephone(xml_content)
    assert result == {
        "parties": [
            {
                "id": "ORG-0001",
                "beneficialOwners": [{"id": "UBO-0001", "telephone": "+123 4567890"}],
            }
        ]
    }


def test_merge_ubo_telephone() -> None:
    release_json = {
        "parties": [
            {
                "id": "ORG-0001",
                "name": "Test Organization",
                "beneficialOwners": [{"id": "UBO-0001", "name": "John Doe"}],
            }
        ]
    }

    ubo_telephone_data = {
        "parties": [
            {
                "id": "ORG-0001",
                "beneficialOwners": [{"id": "UBO-0001", "telephone": "+123 4567890"}],
            }
        ]
    }

    merge_ubo_telephone(release_json, ubo_telephone_data)

    assert release_json == {
        "parties": [
            {
                "id": "ORG-0001",
                "name": "Test Organization",
                "beneficialOwners": [
                    {"id": "UBO-0001", "name": "John Doe", "telephone": "+123 4567890"}
                ],
            }
        ]
    }


def test_merge_ubo_telephone_new_party() -> None:
    release_json = {"parties": [{"id": "ORG-0001", "name": "Test Organization"}]}

    ubo_telephone_data = {
        "parties": [
            {
                "id": "ORG-0002",
                "beneficialOwners": [{"id": "UBO-0002", "telephone": "+987 6543210"}],
            }
        ]
    }

    merge_ubo_telephone(release_json, ubo_telephone_data)

    assert release_json == {
        "parties": [
            {"id": "ORG-0001", "name": "Test Organization"},
            {
                "id": "ORG-0002",
                "beneficialOwners": [{"id": "UBO-0002", "telephone": "+987 6543210"}],
            },
        ]
    }
