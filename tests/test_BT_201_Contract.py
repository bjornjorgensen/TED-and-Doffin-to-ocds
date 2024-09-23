# tests/test_BT_201_Contract.py

from ted_and_doffin_to_ocds.converters.BT_201_Contract import (
    parse_contract_modification_description,
    merge_contract_modification_description,
)


def test_parse_contract_modification_description():
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
          xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
          xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1">
        <efac:ContractModification>
            <efac:Change>
                <efac:ChangedSection>
                    <efbc:ChangedSectionIdentifier>CON-0001</efbc:ChangedSectionIdentifier>
                </efac:ChangedSection>
            </efac:Change>
            <efac:ChangeReason>
                <efbc:ReasonDescription languageID="ENG">The original business case was scoped as a technology replacement programme for a single system. Analysis in the early stages of the programme indicated that two core enterprise systems should be replaced. In order to maximise benefit for these systems replacement activities, it was agreed that the organisation should consider people and process in addition to systems replacement, and work has been re-scoped to accommodate this.</efbc:ReasonDescription>
            </efac:ChangeReason>
        </efac:ContractModification>
        <efac:NoticeResult>
            <efac:LotResult>
                <cbc:ID schemeName="result">RES-0001</cbc:ID>
                <efac:SettledContract>
                    <cbc:ID schemeName="contract">CON-0001</cbc:ID>
                </efac:SettledContract>
            </efac:LotResult>
        </efac:NoticeResult>
    </root>
    """

    result = parse_contract_modification_description(xml_content)

    assert result is not None
    assert "contracts" in result
    assert len(result["contracts"]) == 1

    contract = result["contracts"][0]
    assert contract["id"] == "CON-0001"
    assert "amendments" in contract
    assert len(contract["amendments"]) == 1

    amendment = contract["amendments"][0]
    assert "id" in amendment
    assert "rationale" in amendment
    assert amendment["rationale"].startswith(
        "The original business case was scoped as a technology replacement programme",
    )

    assert contract["awardID"] == "RES-0001"


def test_merge_contract_modification_description():
    existing_json = {"contracts": [{"id": "CON-0001", "awardID": "RES-0001"}]}

    modification_data = {
        "contracts": [
            {
                "id": "CON-0001",
                "amendments": [{"id": "1", "rationale": "New rationale description"}],
            },
        ],
    }

    merge_contract_modification_description(existing_json, modification_data)

    assert len(existing_json["contracts"]) == 1
    contract = existing_json["contracts"][0]
    assert contract["id"] == "CON-0001"
    assert "amendments" in contract
    assert len(contract["amendments"]) == 1
    assert contract["amendments"][0]["rationale"] == "New rationale description"
    assert contract["awardID"] == "RES-0001"
