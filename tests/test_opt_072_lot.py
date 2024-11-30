# tests/test_opt_072_lot.py

from ted_and_doffin_to_ocds.converters.opt_072_lot import (
    merge_quality_target_description,
    parse_quality_target_description,
)


def test_parse_quality_target_description() -> None:
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:TenderingTerms>
                <cac:ContractExecutionRequirement>
                    <cbc:ExecutionRequirementCode listName="customer-service">clean</cbc:ExecutionRequirementCode>
                    <cbc:Description languageID="ENG">A description as given in OPT-072</cbc:Description>
                </cac:ContractExecutionRequirement>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </root>
    """
    result = parse_quality_target_description(xml_content)
    assert result == {
        "tender": {
            "lots": [
                {
                    "id": "LOT-0001",
                    "contractTerms": {
                        "customerServices": [
                            {"description": "A description as given in OPT-072"}
                        ]
                    },
                }
            ]
        }
    }


def test_merge_quality_target_description() -> None:
    release_json = {
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
    quality_target_description_data = {
        "tender": {
            "lots": [
                {
                    "id": "LOT-0001",
                    "contractTerms": {
                        "customerServices": [
                            {"description": "A description as given in OPT-072"}
                        ]
                    },
                }
            ]
        }
    }
    merge_quality_target_description(release_json, quality_target_description_data)
    assert release_json == {
        "tender": {
            "lots": [
                {
                    "id": "LOT-0001",
                    "contractTerms": {
                        "customerServices": [
                            {
                                "type": "clean",
                                "name": "Cleanliness of rolling stock and station facilities",
                                "description": "A description as given in OPT-072",
                            }
                        ]
                    },
                }
            ]
        }
    }
