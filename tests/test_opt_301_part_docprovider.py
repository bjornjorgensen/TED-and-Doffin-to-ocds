# tests/test_opt_301_part_docprovider.py

from ted_and_doffin_to_ocds.converters.opt_301_part_docprovider import (
    part_parse_document_provider,
    part_merge_document_provider,
)


def test_parse_document_provider():
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Part">1</cbc:ID>
            <cac:TenderingTerms>
                <cac:DocumentProviderParty>
                    <cac:PartyIdentification>
                        <cbc:ID schemeName="touchpoint">TPO-0001</cbc:ID>
                    </cac:PartyIdentification>
                </cac:DocumentProviderParty>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </root>
    """
    result = part_parse_document_provider(xml_content)
    assert result == {"parties": [{"id": "TPO-0001", "roles": ["processContactPoint"]}]}


def test_merge_document_provider():
    release_json = {"parties": [{"id": "TPO-0001", "roles": ["buyer"]}]}
    document_provider_data = {
        "parties": [{"id": "TPO-0001", "roles": ["processContactPoint"]}]
    }
    part_merge_document_provider(release_json, document_provider_data)
    assert release_json == {
        "parties": [{"id": "TPO-0001", "roles": ["buyer", "processContactPoint"]}]
    }


def test_merge_document_provider_new_party():
    release_json = {"parties": [{"id": "ORG-0001", "roles": ["buyer"]}]}
    document_provider_data = {
        "parties": [{"id": "TPO-0001", "roles": ["processContactPoint"]}]
    }
    part_merge_document_provider(release_json, document_provider_data)
    assert release_json == {
        "parties": [
            {"id": "ORG-0001", "roles": ["buyer"]},
            {"id": "TPO-0001", "roles": ["processContactPoint"]},
        ]
    }
