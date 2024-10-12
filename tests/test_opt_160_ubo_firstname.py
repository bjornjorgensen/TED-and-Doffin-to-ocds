# tests/test_opt_160_ubo_firstname.py

from ted_and_doffin_to_ocds.converters.opt_160_ubo_firstname import (
    parse_ubo_firstname,
    merge_ubo_firstname,
)


def test_parse_ubo_firstname():
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
          xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1">
        <ext:UBLExtensions>
            <ext:UBLExtension>
                <ext:ExtensionContent>
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
                                <cbc:FirstName>Mickey</cbc:FirstName>
                            </efac:UltimateBeneficialOwner>
                        </efac:Organizations>
                    </efext:EformsExtension>
                </ext:ExtensionContent>
            </ext:UBLExtension>
        </ext:UBLExtensions>
    </root>
    """

    result = parse_ubo_firstname(xml_content)

    assert result is not None
    assert "parties" in result
    assert len(result["parties"]) == 1

    party = result["parties"][0]
    assert party["id"] == "ORG-0001"
    assert "beneficialOwners" in party
    assert len(party["beneficialOwners"]) == 1

    bo = party["beneficialOwners"][0]
    assert bo["id"] == "UBO-0001"
    assert bo["name"] == "Mickey"


def test_merge_ubo_firstname():
    release_json = {"parties": []}
    ubo_data = {
        "parties": [
            {
                "id": "ORG-0001",
                "beneficialOwners": [{"id": "UBO-0001", "name": "Mickey"}],
            }
        ]
    }

    merge_ubo_firstname(release_json, ubo_data)

    assert "parties" in release_json
    assert len(release_json["parties"]) == 1

    party = release_json["parties"][0]
    assert party["id"] == "ORG-0001"
    assert "beneficialOwners" in party
    assert len(party["beneficialOwners"]) == 1

    bo = party["beneficialOwners"][0]
    assert bo["id"] == "UBO-0001"
    assert bo["name"] == "Mickey"


def test_merge_ubo_firstname_existing_party():
    release_json = {
        "parties": [
            {
                "id": "ORG-0001",
                "beneficialOwners": [{"id": "UBO-0001", "name": "Donald"}],
            }
        ]
    }
    ubo_data = {
        "parties": [
            {
                "id": "ORG-0001",
                "beneficialOwners": [{"id": "UBO-0001", "name": "Mickey"}],
            }
        ]
    }

    merge_ubo_firstname(release_json, ubo_data)

    assert len(release_json["parties"]) == 1

    party = release_json["parties"][0]
    assert party["id"] == "ORG-0001"
    assert len(party["beneficialOwners"]) == 1

    bo = party["beneficialOwners"][0]
    assert bo["id"] == "UBO-0001"
    assert bo["name"] == "Mickey"
