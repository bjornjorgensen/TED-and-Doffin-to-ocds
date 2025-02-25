# tests/test_opt_301_part_addinfo.py

from src.ted_and_doffin_to_ocds.converters.eforms.opt_301_part_addinfo import (
    part_merge_additional_info_provider,
    part_parse_additional_info_provider,
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
    result = part_parse_additional_info_provider(xml_content)
    assert result == {"parties": [{"id": "TPO-0001", "roles": ["processContactPoint"]}]}


def test_merge_additional_info_provider() -> None:
    release_json = {"parties": [{"id": "TPO-0001", "roles": ["buyer"]}]}
    additional_info_data = {
        "parties": [{"id": "TPO-0001", "roles": ["processContactPoint"]}]
    }
    part_merge_additional_info_provider(release_json, additional_info_data)
    assert release_json == {
        "parties": [{"id": "TPO-0001", "roles": ["buyer", "processContactPoint"]}]
    }


def test_merge_additional_info_provider_new_party() -> None:
    release_json = {"parties": [{"id": "ORG-0001", "roles": ["buyer"]}]}
    additional_info_data = {
        "parties": [{"id": "TPO-0001", "roles": ["processContactPoint"]}]
    }
    part_merge_additional_info_provider(release_json, additional_info_data)
    assert release_json == {
        "parties": [
            {"id": "ORG-0001", "roles": ["buyer"]},
            {"id": "TPO-0001", "roles": ["processContactPoint"]},
        ]
    }
