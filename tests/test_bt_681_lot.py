import pytest

from src.ted_and_doffin_to_ocds.converters.eforms.bt_681_lot import (
    merge_foreign_subsidies_regulation,
    parse_foreign_subsidies_regulation,
)


def test_parse_foreign_subsidies_regulation():
    xml_content = """
    <cac:ProcurementProjectLot xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
                               xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
        <cac:TenderingTerms>
            <cac:ContractExecutionRequirement>
                <cbc:ExecutionRequirementCode listName="fsr">true</cbc:ExecutionRequirementCode>
            </cac:ContractExecutionRequirement>
        </cac:TenderingTerms>
    </cac:ProcurementProjectLot>
    """
    expected_result = {
        "tender": {
            "lots": [
                {
                    "id": "LOT-0001",
                    "coveredBy": ["EU-FSR"],
                }
            ]
        }
    }
    result = parse_foreign_subsidies_regulation(xml_content)
    assert result == expected_result


def test_merge_foreign_subsidies_regulation():
    release_json = {
        "tender": {
            "lots": [
                {
                    "id": "LOT-0001",
                }
            ]
        }
    }
    fsr_data = {
        "tender": {
            "lots": [
                {
                    "id": "LOT-0001",
                    "coveredBy": ["EU-FSR"],
                }
            ]
        }
    }
    merge_foreign_subsidies_regulation(release_json, fsr_data)
    expected_result = {
        "tender": {
            "lots": [
                {
                    "id": "LOT-0001",
                    "coveredBy": ["EU-FSR"],
                }
            ]
        }
    }
    assert release_json == expected_result


if __name__ == "__main__":
    pytest.main()
