# tests/test_opt_301_part_addinfo.py

from src.ted_and_doffin_to_ocds.converters.eforms.opt_301_part_addinfo import (
    merge_additional_info_provider_part,
    parse_additional_info_provider_part,
)


def test_parse_additional_info_provider() -> None:
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Part">1</cbc:ID>
            <cac:TenderingTerms>
                <cac:AdditionalInformationParty>
                    <cac:PartyIdentification>
                        <cbc:ID schemeName="touchpoint">TPO-0001</cbc:ID>
                    </cac:PartyIdentification>
                </cac:AdditionalInformationParty>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </root>
    """
    result = parse_additional_info_provider_part(xml_content)
    assert result == {"parties": [{"id": "TPO-0001", "roles": ["processContactPoint"]}]}


def test_parse_additional_info_provider_with_org_id() -> None:
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Part">1</cbc:ID>
            <cac:TenderingTerms>
                <cac:AdditionalInformationParty>
                    <cac:PartyIdentification>
                        <cbc:ID>ORG-0002</cbc:ID>
                    </cac:PartyIdentification>
                </cac:AdditionalInformationParty>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </root>
    """
    result = parse_additional_info_provider_part(xml_content)
    assert result == {"parties": [{"id": "ORG-0002", "roles": ["processContactPoint"]}]}


def test_parse_additional_info_provider_with_invalid_id() -> None:
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Part">1</cbc:ID>
            <cac:TenderingTerms>
                <cac:AdditionalInformationParty>
                    <cac:PartyIdentification>
                        <cbc:ID>INVALID-ID</cbc:ID>
                    </cac:PartyIdentification>
                </cac:AdditionalInformationParty>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </root>
    """
    result = parse_additional_info_provider_part(xml_content)
    assert result is None


def test_merge_additional_info_provider() -> None:
    release_json = {"parties": [{"id": "TPO-0001", "roles": ["buyer"]}]}
    additional_info_data = {
        "parties": [{"id": "TPO-0001", "roles": ["processContactPoint"]}]
    }
    merge_additional_info_provider_part(release_json, additional_info_data)
    assert release_json == {
        "parties": [{"id": "TPO-0001", "roles": ["buyer", "processContactPoint"]}]
    }


def test_merge_additional_info_provider_new_party() -> None:
    release_json = {"parties": [{"id": "ORG-0001", "roles": ["buyer"]}]}
    additional_info_data = {
        "parties": [{"id": "TPO-0001", "roles": ["processContactPoint"]}]
    }
    merge_additional_info_provider_part(release_json, additional_info_data)
    assert release_json == {
        "parties": [
            {"id": "ORG-0001", "roles": ["buyer"]},
            {"id": "TPO-0001", "roles": ["processContactPoint"]},
        ]
    }
