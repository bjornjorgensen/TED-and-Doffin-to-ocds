# tests/test_opt_315_lotresult.py

from ted_and_doffin_to_ocds.converters.opt_315_lotresult import (
    merge_contract_identifier_reference,
    parse_contract_identifier_reference,
)


def test_parse_contract_identifier_reference() -> None:
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
          xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1">
        <efac:NoticeResult>
            <efac:SettledContract>
                <cbc:ID schemeName="contract">CON-0001</cbc:ID>
            </efac:SettledContract>
            <efac:LotResult>
                <cbc:ID schemeName="result">RES-0001</cbc:ID>
                <efac:SettledContract>
                    <cbc:ID schemeName="contract">CON-0001</cbc:ID>
                </efac:SettledContract>
            </efac:LotResult>
        </efac:NoticeResult>
    </root>
    """
    result = parse_contract_identifier_reference(xml_content)
    assert result == {"contracts": [{"id": "CON-0001", "awardID": "RES-0001"}]}


def test_merge_contract_identifier_reference() -> None:
    release_json = {"contracts": [{"id": "CON-0001", "title": "Existing Contract"}]}
    contract_identifier_data = {
        "contracts": [{"id": "CON-0001", "awardID": "RES-0001"}]
    }
    merge_contract_identifier_reference(release_json, contract_identifier_data)
    assert release_json == {
        "contracts": [
            {"id": "CON-0001", "title": "Existing Contract", "awardID": "RES-0001"}
        ]
    }


def test_merge_contract_identifier_reference_new_contract() -> None:
    release_json = {"contracts": [{"id": "CON-0002", "title": "Existing Contract"}]}
    contract_identifier_data = {
        "contracts": [{"id": "CON-0001", "awardID": "RES-0001"}]
    }
    merge_contract_identifier_reference(release_json, contract_identifier_data)
    assert release_json == {
        "contracts": [
            {"id": "CON-0002", "title": "Existing Contract"},
            {"id": "CON-0001", "awardID": "RES-0001"},
        ]
    }


def test_merge_contract_identifier_reference_no_data() -> None:
    release_json = {"contracts": [{"id": "CON-0001", "title": "Existing Contract"}]}
    merge_contract_identifier_reference(release_json, None)
    assert release_json == {
        "contracts": [{"id": "CON-0001", "title": "Existing Contract"}]
    }
