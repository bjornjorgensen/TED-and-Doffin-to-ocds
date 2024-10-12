# tests/test_opt_202_ubo.py

from ted_and_doffin_to_ocds.converters.opt_202_ubo import (
    parse_beneficial_owner_identifier,
    merge_beneficial_owner_identifier,
)


def test_parse_beneficial_owner_identifier():
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
                            </efac:UltimateBeneficialOwner>
                        </efac:Organizations>
                    </efext:EformsExtension>
                </ext:ExtensionContent>
            </ext:UBLExtension>
        </ext:UBLExtensions>
    </root>
    """

    result = parse_beneficial_owner_identifier(xml_content)

    assert result is not None
    assert "parties" in result
    assert len(result["parties"]) == 1
    assert result["parties"][0]["id"] == "ORG-0001"
    assert "beneficialOwners" in result["parties"][0]
    assert len(result["parties"][0]["beneficialOwners"]) == 1
    assert result["parties"][0]["beneficialOwners"][0]["id"] == "UBO-0001"


def test_merge_beneficial_owner_identifier():
    release_json = {"parties": []}
    ubo_data = {
        "parties": [{"id": "ORG-0001", "beneficialOwners": [{"id": "UBO-0001"}]}]
    }

    merge_beneficial_owner_identifier(release_json, ubo_data)

    assert "parties" in release_json
    assert len(release_json["parties"]) == 1
    assert release_json["parties"][0]["id"] == "ORG-0001"
    assert "beneficialOwners" in release_json["parties"][0]
    assert len(release_json["parties"][0]["beneficialOwners"]) == 1
    assert release_json["parties"][0]["beneficialOwners"][0]["id"] == "UBO-0001"


def test_merge_beneficial_owner_identifier_existing_party():
    release_json = {
        "parties": [
            {
                "id": "ORG-0001",
                "name": "Existing Organization",
                "beneficialOwners": [{"id": "UBO-0001", "name": "Existing UBO"}],
            }
        ]
    }
    ubo_data = {
        "parties": [
            {
                "id": "ORG-0001",
                "beneficialOwners": [{"id": "UBO-0001"}, {"id": "UBO-0002"}],
            }
        ]
    }

    merge_beneficial_owner_identifier(release_json, ubo_data)

    assert len(release_json["parties"]) == 1
    assert release_json["parties"][0]["id"] == "ORG-0001"
    assert release_json["parties"][0]["name"] == "Existing Organization"
    assert len(release_json["parties"][0]["beneficialOwners"]) == 2
    assert release_json["parties"][0]["beneficialOwners"][0]["id"] == "UBO-0001"
    assert release_json["parties"][0]["beneficialOwners"][0]["name"] == "Existing UBO"
    assert release_json["parties"][0]["beneficialOwners"][1]["id"] == "UBO-0002"
