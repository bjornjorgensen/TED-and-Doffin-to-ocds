# tests/test_opt_301_lot_mediator.py

import pytest
from ted_and_doffin_to_ocds.converters.opt_301_lot_mediator import (
    parse_mediator_technical_identifier,
    merge_mediator_technical_identifier,
)


@pytest.fixture
def sample_xml():
    return """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:TenderingTerms>
                <cac:AppealTerms>
                    <cac:MediationParty>
                        <cac:PartyIdentification>
                            <cbc:ID schemeName="touchpoint">TPO-0005</cbc:ID>
                        </cac:PartyIdentification>
                    </cac:MediationParty>
                </cac:AppealTerms>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </root>
    """


def test_parse_mediator_technical_identifier(sample_xml):
    result = parse_mediator_technical_identifier(sample_xml)
    assert result is not None
    assert "parties" in result
    assert len(result["parties"]) == 1
    assert result["parties"][0]["id"] == "TPO-0005"
    assert result["parties"][0]["roles"] == ["mediationBody"]


def test_merge_mediator_technical_identifier():
    mediator_data = {"parties": [{"id": "TPO-0005", "roles": ["mediationBody"]}]}
    release_json = {}
    merge_mediator_technical_identifier(release_json, mediator_data)
    assert "parties" in release_json
    assert len(release_json["parties"]) == 1
    assert release_json["parties"][0]["id"] == "TPO-0005"
    assert release_json["parties"][0]["roles"] == ["mediationBody"]


def test_merge_mediator_technical_identifier_existing_party():
    mediator_data = {"parties": [{"id": "TPO-0005", "roles": ["mediationBody"]}]}
    release_json = {"parties": [{"id": "TPO-0005", "roles": ["buyer"]}]}
    merge_mediator_technical_identifier(release_json, mediator_data)
    assert len(release_json["parties"]) == 1
    assert release_json["parties"][0]["id"] == "TPO-0005"
    assert set(release_json["parties"][0]["roles"]) == {"buyer", "mediationBody"}


def test_parse_mediator_technical_identifier_no_data():
    xml_content = "<root></root>"
    result = parse_mediator_technical_identifier(xml_content)
    assert result is None


def test_merge_mediator_technical_identifier_no_data():
    release_json = {}
    merge_mediator_technical_identifier(release_json, None)
    assert release_json == {}
