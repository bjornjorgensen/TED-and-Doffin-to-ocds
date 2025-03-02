# tests/test_bt_5423_Lot.py

from src.ted_and_doffin_to_ocds.converters.eforms.bt_5423_lot import (
    merge_award_criterion_number_threshold_lot,
    parse_award_criterion_number_threshold_lot,
)


def create_xml_with_award_criterion(lot_id, threshold_code) -> str:
    return f"""
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
          xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
          xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">{lot_id}</cbc:ID>
            <cac:TenderingTerms>
                <cac:AwardingTerms>
                    <cac:AwardingCriterion>
                        <cac:SubordinateAwardingCriterion>
                            <ext:UBLExtensions>
                                <ext:UBLExtension>
                                    <ext:ExtensionContent>
                                        <efext:EformsExtension>
                                            <efac:AwardCriterionParameter>
                                                <efbc:ParameterCode listName="number-threshold">{threshold_code}</efbc:ParameterCode>
                                            </efac:AwardCriterionParameter>
                                        </efext:EformsExtension>
                                    </ext:ExtensionContent>
                                </ext:UBLExtension>
                            </ext:UBLExtensions>
                        </cac:SubordinateAwardingCriterion>
                    </cac:AwardingCriterion>
                </cac:AwardingTerms>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </root>
    """


def create_xml_with_multiple_criteria(lot_id, threshold_codes) -> str:
    """Create XML with multiple SubordinateAwardingCriterion elements."""
    criteria_xml = ""
    for code in threshold_codes:
        criteria_xml += f"""
        <cac:SubordinateAwardingCriterion>
            <ext:UBLExtensions>
                <ext:UBLExtension>
                    <ext:ExtensionContent>
                        <efext:EformsExtension>
                            <efac:AwardCriterionParameter>
                                <efbc:ParameterCode listName="number-threshold">{code}</efbc:ParameterCode>
                            </efac:AwardCriterionParameter>
                        </efext:EformsExtension>
                    </ext:ExtensionContent>
                </ext:UBLExtension>
            </ext:UBLExtensions>
        </cac:SubordinateAwardingCriterion>
        """
    
    return f"""
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
          xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
          xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">{lot_id}</cbc:ID>
            <cac:TenderingTerms>
                <cac:AwardingTerms>
                    <cac:AwardingCriterion>
                        {criteria_xml}
                    </cac:AwardingCriterion>
                </cac:AwardingTerms>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </root>
    """


def test_parse_award_criterion_number_threshold_max_pass() -> None:
    xml_content = create_xml_with_award_criterion("LOT-001", "max-pass")
    result = parse_award_criterion_number_threshold_lot(xml_content)

    assert result is not None
    assert result["tender"]["lots"][0]["id"] == "LOT-001"
    assert (
        result["tender"]["lots"][0]["awardCriteria"]["criteria"][0]["numbers"][0][
            "threshold"
        ]
        == "maximumBids"
    )


def test_parse_award_criterion_number_threshold_min_score() -> None:
    xml_content = create_xml_with_award_criterion("LOT-002", "min-score")
    result = parse_award_criterion_number_threshold_lot(xml_content)

    assert result is not None
    assert result["tender"]["lots"][0]["id"] == "LOT-002"
    assert (
        result["tender"]["lots"][0]["awardCriteria"]["criteria"][0]["numbers"][0][
            "threshold"
        ]
        == "minimumScore"
    )


def test_parse_award_criterion_number_threshold_invalid_code() -> None:
    xml_content = create_xml_with_award_criterion("LOT-003", "invalid-code")
    result = parse_award_criterion_number_threshold_lot(xml_content)

    # Now we expect an empty result since the invalid code is filtered out
    assert result is None


def test_parse_award_criterion_number_threshold_no_data() -> None:
    xml_content = "<root></root>"
    result = parse_award_criterion_number_threshold_lot(xml_content)

    assert result is None


def test_parse_award_criterion_multiple_criteria() -> None:
    """Test parsing XML with multiple SubordinateAwardingCriterion elements."""
    xml_content = create_xml_with_multiple_criteria("LOT-004", ["max-pass", "min-score"])
    result = parse_award_criterion_number_threshold_lot(xml_content)

    assert result is not None
    assert result["tender"]["lots"][0]["id"] == "LOT-004"
    assert len(result["tender"]["lots"][0]["awardCriteria"]["criteria"]) == 2
    
    # Check first criterion has maximumBids threshold
    assert result["tender"]["lots"][0]["awardCriteria"]["criteria"][0]["numbers"][0]["threshold"] == "maximumBids"
    
    # Check second criterion has minimumScore threshold
    assert result["tender"]["lots"][0]["awardCriteria"]["criteria"][1]["numbers"][0]["threshold"] == "minimumScore"


def test_parse_award_criterion_mixed_valid_invalid() -> None:
    """Test parsing XML with a mix of valid and invalid threshold codes."""
    xml_content = create_xml_with_multiple_criteria("LOT-005", ["max-pass", "invalid-code", "min-score"])
    result = parse_award_criterion_number_threshold_lot(xml_content)

    assert result is not None
    assert result["tender"]["lots"][0]["id"] == "LOT-005"
    # Only the valid codes should create criteria
    assert len(result["tender"]["lots"][0]["awardCriteria"]["criteria"]) == 2
    
    thresholds = [
        criterion["numbers"][0]["threshold"] 
        for criterion in result["tender"]["lots"][0]["awardCriteria"]["criteria"]
    ]
    assert "maximumBids" in thresholds
    assert "minimumScore" in thresholds


def test_merge_award_criterion_number_threshold() -> None:
    existing_release = {
        "tender": {
            "lots": [
                {
                    "id": "LOT-001",
                    "awardCriteria": {"criteria": [{"id": "AC-1", "numbers": []}]},
                },
            ],
        },
    }

    new_data = {
        "tender": {
            "lots": [
                {
                    "id": "LOT-001",
                    "awardCriteria": {
                        "criteria": [{"numbers": [{"threshold": "maximumBids"}]}],
                    },
                },
            ],
        },
    }

    merge_award_criterion_number_threshold_lot(existing_release, new_data)

    assert len(existing_release["tender"]["lots"]) == 1
    assert len(existing_release["tender"]["lots"][0]["awardCriteria"]["criteria"]) == 1
    assert (
        len(
            existing_release["tender"]["lots"][0]["awardCriteria"]["criteria"][0][
                "numbers"
            ],
        )
        == 1
    )
    assert (
        existing_release["tender"]["lots"][0]["awardCriteria"]["criteria"][0][
            "numbers"
        ][0]["threshold"]
        == "maximumBids"
    )


def test_merge_award_criterion_number_threshold_new_lot() -> None:
    existing_release = {"tender": {"lots": []}}

    new_data = {
        "tender": {
            "lots": [
                {
                    "id": "LOT-001",
                    "awardCriteria": {
                        "criteria": [{"numbers": [{"threshold": "minimumScore"}]}],
                    },
                },
            ],
        },
    }

    merge_award_criterion_number_threshold_lot(existing_release, new_data)

    assert len(existing_release["tender"]["lots"]) == 1
    assert existing_release["tender"]["lots"][0]["id"] == "LOT-001"
    assert (
        existing_release["tender"]["lots"][0]["awardCriteria"]["criteria"][0][
            "numbers"
        ][0]["threshold"]
        == "minimumScore"
    )


def test_merge_award_criterion_number_threshold_no_data() -> None:
    existing_release = {"tender": {"lots": []}}
    merge_award_criterion_number_threshold_lot(existing_release, None)
    assert existing_release == {"tender": {"lots": []}}


def test_merge_award_criterion_multiple_criteria() -> None:
    """Test merging data with multiple criteria per lot."""
    existing_release = {
        "tender": {
            "lots": [
                {
                    "id": "LOT-004",
                    "awardCriteria": {"criteria": []},
                },
            ],
        },
    }

    new_data = {
        "tender": {
            "lots": [
                {
                    "id": "LOT-004",
                    "awardCriteria": {
                        "criteria": [
                            {"numbers": [{"threshold": "maximumBids"}]},
                            {"numbers": [{"threshold": "minimumScore"}]},
                        ],
                    },
                },
            ],
        },
    }

    merge_award_criterion_number_threshold_lot(existing_release, new_data)

    assert len(existing_release["tender"]["lots"]) == 1
    assert len(existing_release["tender"]["lots"][0]["awardCriteria"]["criteria"]) == 2
    
    # Check that both criteria were merged correctly
    thresholds = [
        criterion["numbers"][0]["threshold"] 
        for criterion in existing_release["tender"]["lots"][0]["awardCriteria"]["criteria"]
    ]
    assert "maximumBids" in thresholds
    assert "minimumScore" in thresholds
