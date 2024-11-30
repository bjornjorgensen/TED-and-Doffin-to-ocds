# tests/test_bt_200_Contract.py

from ted_and_doffin_to_ocds.converters.bt_200_contract import (
    merge_contract_modification_reason,
    parse_contract_modification_reason,
)


def test_parse_contract_modification_reason() -> None:
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
                <cbc:ReasonCode listName="modification-justification">MJ001</cbc:ReasonCode>
            </efac:ChangeReason>
        </efac:ContractModification>
        <efac:noticeResult>
            <efac:LotResult>
                <cbc:ID schemeName="result">RES-0001</cbc:ID>
                <efac:SettledContract>
                    <cbc:ID schemeName="contract">CON-0001</cbc:ID>
                </efac:SettledContract>
            </efac:LotResult>
        </efac:noticeResult>
    </root>
    """

    result = parse_contract_modification_reason(xml_content)

    assert result is not None
    assert "contracts" in result
    assert len(result["contracts"]) == 1

    contract = result["contracts"][0]
    assert contract["id"] == "CON-0001"
    assert "amendments" in contract
    assert len(contract["amendments"]) == 1

    amendment = contract["amendments"][0]
    assert "id" in amendment
    assert "rationaleClassifications" in amendment
    assert len(amendment["rationaleClassifications"]) == 1

    rationale = amendment["rationaleClassifications"][0]
    assert rationale["id"] == "MJ001"
    assert (
        rationale["description"]
        == "Need for additional works, services or supplies by the original contractor."
    )
    assert rationale["scheme"] == "Modification justification"

    assert contract["awardID"] == "RES-0001"


def test_parse_contract_modification_reason_multiple_awards() -> None:
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
                    <efbc:ChangedSectionIdentifier>CON-0002</efbc:ChangedSectionIdentifier>
                </efac:ChangedSection>
            </efac:Change>
            <efac:ChangeReason>
                <cbc:ReasonCode listName="modification-justification">MJ002</cbc:ReasonCode>
            </efac:ChangeReason>
        </efac:ContractModification>
        <efac:noticeResult>
            <efac:LotResult>
                <cbc:ID schemeName="result">RES-0002</cbc:ID>
                <efac:SettledContract>
                    <cbc:ID schemeName="contract">CON-0002</cbc:ID>
                </efac:SettledContract>
            </efac:LotResult>
            <efac:LotResult>
                <cbc:ID schemeName="result">RES-0003</cbc:ID>
                <efac:SettledContract>
                    <cbc:ID schemeName="contract">CON-0002</cbc:ID>
                </efac:SettledContract>
            </efac:LotResult>
        </efac:noticeResult>
    </root>
    """

    result = parse_contract_modification_reason(xml_content)

    assert result is not None
    assert "contracts" in result
    assert len(result["contracts"]) == 1

    contract = result["contracts"][0]
    assert contract["id"] == "CON-0002"
    assert "amendments" in contract
    assert len(contract["amendments"]) == 1

    amendment = contract["amendments"][0]
    assert "id" in amendment
    assert "rationaleClassifications" in amendment
    assert len(amendment["rationaleClassifications"]) == 1

    rationale = amendment["rationaleClassifications"][0]
    assert rationale["id"] == "MJ002"
    assert (
        rationale["description"]
        == "Need for modifications because of circumstances which a diligent buyer could not predict."
    )
    assert rationale["scheme"] == "Modification justification"

    assert "awardIDs" in contract
    assert set(contract["awardIDs"]) == {"RES-0002", "RES-0003"}


def test_merge_contract_modification_reason() -> None:
    existing_json = {"contracts": [{"id": "CON-0001", "awardID": "RES-0001"}]}

    modification_data = {
        "contracts": [
            {
                "id": "CON-0001",
                "amendments": [
                    {
                        "id": "1",
                        "rationaleClassifications": [
                            {
                                "id": "MJ001",
                                "description": "Need for additional works, services or supplies by the original contractor.",
                                "scheme": "Modification justification",
                            },
                        ],
                    },
                ],
            },
        ],
    }

    merge_contract_modification_reason(existing_json, modification_data)

    assert len(existing_json["contracts"]) == 1
    contract = existing_json["contracts"][0]
    assert contract["id"] == "CON-0001"
    assert "amendments" in contract
    assert len(contract["amendments"]) == 1
    assert contract["amendments"][0]["rationaleClassifications"][0]["id"] == "MJ001"
    assert contract["awardID"] == "RES-0001"


def test_merge_contract_modification_reason_new_contract() -> None:
    existing_json = {"contracts": [{"id": "CON-0001", "awardID": "RES-0001"}]}

    modification_data = {
        "contracts": [
            {
                "id": "CON-0002",
                "amendments": [
                    {
                        "id": "1",
                        "rationaleClassifications": [
                            {
                                "id": "MJ002",
                                "description": "Need for modifications because of circumstances which a diligent buyer could not predict.",
                                "scheme": "Modification justification",
                            },
                        ],
                    },
                ],
                "awardID": "RES-0002",
            },
        ],
    }

    merge_contract_modification_reason(existing_json, modification_data)

    assert len(existing_json["contracts"]) == 2
    new_contract = existing_json["contracts"][1]
    assert new_contract["id"] == "CON-0002"
    assert "amendments" in new_contract
    assert len(new_contract["amendments"]) == 1
    assert new_contract["amendments"][0]["rationaleClassifications"][0]["id"] == "MJ002"
    assert new_contract["awardID"] == "RES-0002"
