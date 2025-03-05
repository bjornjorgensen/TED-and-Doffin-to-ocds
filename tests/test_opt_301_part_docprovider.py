# tests/test_opt_301_part_docprovider.py

from src.ted_and_doffin_to_ocds.converters.eforms.opt_301_part_docprovider import (
    merge_document_provider_part,
    parse_document_provider_part,
)


def test_parse_document_provider() -> None:
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
    result = parse_document_provider_part(xml_content)
    assert result == {"parties": [{"id": "TPO-0001", "roles": ["processContactPoint"]}]}


def test_merge_document_provider() -> None:
    release_json = {"parties": [{"id": "TPO-0001", "roles": ["buyer"]}]}
    document_provider_data = {
        "parties": [{"id": "TPO-0001", "roles": ["processContactPoint"]}]
    }
    merge_document_provider_part(release_json, document_provider_data)
    assert release_json == {
        "parties": [{"id": "TPO-0001", "roles": ["buyer", "processContactPoint"]}]
    }


def test_merge_document_provider_new_party() -> None:
    release_json = {"parties": [{"id": "ORG-0001", "roles": ["buyer"]}]}
    document_provider_data = {
        "parties": [{"id": "TPO-0001", "roles": ["processContactPoint"]}]
    }
    merge_document_provider_part(release_json, document_provider_data)
    assert release_json == {
        "parties": [
            {"id": "ORG-0001", "roles": ["buyer"]},
            {"id": "TPO-0001", "roles": ["processContactPoint"]},
        ]
    }
