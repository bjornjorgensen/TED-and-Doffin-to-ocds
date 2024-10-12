# tests/test_opt_030_procedure_sprovider.py

from ted_and_doffin_to_ocds.converters.opt_030_procedure_sprovider import (
    parse_provided_service_type,
    merge_provided_service_type,
)


def test_parse_provided_service_type():
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ContractingParty>
            <cac:Party>
                <cac:ServiceProviderParty>
                    <cbc:ServiceTypeCode listName="organisation-role">ted-esen</cbc:ServiceTypeCode>
                    <cac:Party>
                        <cac:PartyIdentification>
                            <cbc:ID>ORG-0001</cbc:ID>
                        </cac:PartyIdentification>
                    </cac:Party>
                </cac:ServiceProviderParty>
            </cac:Party>
        </cac:ContractingParty>
    </root>
    """
    result = parse_provided_service_type(xml_content)
    assert result == {"parties": [{"id": "ORG-0001", "roles": ["eSender"]}]}


def test_merge_provided_service_type():
    release_json = {"parties": [{"id": "ORG-0001", "name": "Existing Organization"}]}
    provided_service_type_data = {"parties": [{"id": "ORG-0001", "roles": ["eSender"]}]}
    merge_provided_service_type(release_json, provided_service_type_data)
    assert release_json == {
        "parties": [
            {"id": "ORG-0001", "name": "Existing Organization", "roles": ["eSender"]}
        ]
    }
