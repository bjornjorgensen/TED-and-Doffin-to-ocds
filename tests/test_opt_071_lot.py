# tests/test_opt_071_lot.py

from src.ted_and_doffin_to_ocds.converters.eforms.opt_071_lot import (
    merge_quality_target_code,
    parse_quality_target_code,
)


def test_parse_quality_target_code() -> None:
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:TenderingTerms>
                <cac:ContractExecutionRequirement>
                    <cbc:ExecutionRequirementCode listName="customer-service">clean</cbc:ExecutionRequirementCode>
                </cac:ContractExecutionRequirement>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </root>
    """
    result = parse_quality_target_code(xml_content)
    assert result == {
        "tender": {
            "lots": [
                {
                    "id": "LOT-0001",
                    "contractTerms": {
                        "customerServices": [
                            {
                                "type": "clean",
                                "name": "Cleanliness of rolling stock and station facilities",
                            }
                        ]
                    },
                }
            ]
        }
    }


def test_merge_quality_target_code() -> None:
    release_json = {"tender": {"lots": [{"id": "LOT-0001", "title": "Existing Lot"}]}}
    quality_target_code_data = {
        "tender": {
            "lots": [
                {
                    "id": "LOT-0001",
                    "contractTerms": {
                        "customerServices": [
                            {
                                "type": "clean",
                                "name": "Cleanliness of rolling stock and station facilities",
                            }
                        ]
                    },
                }
            ]
        }
    }
    merge_quality_target_code(release_json, quality_target_code_data)
    assert release_json == {
        "tender": {
            "lots": [
                {
                    "id": "LOT-0001",
                    "title": "Existing Lot",
                    "contractTerms": {
                        "customerServices": [
                            {
                                "type": "clean",
                                "name": "Cleanliness of rolling stock and station facilities",
                            }
                        ]
                    },
                }
            ]
        }
    }
