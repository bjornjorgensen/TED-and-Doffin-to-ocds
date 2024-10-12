# tests/test_opt_300_procedure_sprovider.py

from ted_and_doffin_to_ocds.converters.opt_300_procedure_sprovider import (
    parse_service_provider_identifier,
    merge_service_provider_identifier,
)


def test_parse_service_provider_identifier():
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
          xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1">
        <cac:ContractingParty>
            <cac:Party>
                <cac:ServiceProviderParty>
                    <cac:Party>
                        <cac:PartyIdentification>
                            <cbc:ID>ORG-0001</cbc:ID>
                        </cac:PartyIdentification>
                    </cac:Party>
                </cac:ServiceProviderParty>
            </cac:Party>
        </cac:ContractingParty>
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
                                    <cac:PartyName>
                                        <cbc:Name languageID="ENG">Service Provider Ltd</cbc:Name>
                                    </cac:PartyName>
                                </efac:Company>
                            </efac:Organization>
                        </efac:Organizations>
                    </efext:EformsExtension>
                </ext:ExtensionContent>
            </ext:UBLExtension>
        </ext:UBLExtensions>
    </root>
    """

    result = parse_service_provider_identifier(xml_content)

    assert result is not None
    assert "parties" in result
    assert len(result["parties"]) == 1

    party = result["parties"][0]
    assert party["id"] == "ORG-0001"
    assert party["name"] == "Service Provider Ltd"


def test_merge_service_provider_identifier():
    release_json = {"parties": []}
    provider_data = {"parties": [{"id": "ORG-0001", "name": "Service Provider Ltd"}]}

    merge_service_provider_identifier(release_json, provider_data)

    assert "parties" in release_json
    assert len(release_json["parties"]) == 1

    party = release_json["parties"][0]
    assert party["id"] == "ORG-0001"
    assert party["name"] == "Service Provider Ltd"


def test_merge_service_provider_identifier_existing_party():
    release_json = {"parties": [{"id": "ORG-0001", "name": "Existing Organization"}]}
    provider_data = {"parties": [{"id": "ORG-0001", "name": "Service Provider Ltd"}]}

    merge_service_provider_identifier(release_json, provider_data)

    assert len(release_json["parties"]) == 1

    party = release_json["parties"][0]
    assert party["id"] == "ORG-0001"
    assert party["name"] == "Existing Organization"
