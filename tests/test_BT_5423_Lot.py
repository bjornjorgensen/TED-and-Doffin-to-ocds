# tests/test_bt_5423_Lot.py

from ted_and_doffin_to_ocds.converters.bt_5423_lot import (
    parse_award_criterion_number_threshold,
    merge_award_criterion_number_threshold,
)


def create_xml_with_award_criterion(lot_id, threshold_code):
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


def test_parse_award_criterion_number_threshold_max_pass():
    xml_content = create_xml_with_award_criterion("LOT-001", "max-pass")
    result = parse_award_criterion_number_threshold(xml_content)

    assert result is not None
    assert result["tender"]["lots"][0]["id"] == "LOT-001"
    assert (
        result["tender"]["lots"][0]["awardCriteria"]["criteria"][0]["numbers"][0][
            "threshold"
        ]
        == "maximumBids"
    )


def test_parse_award_criterion_number_threshold_min_score():
    xml_content = create_xml_with_award_criterion("LOT-002", "min-score")
    result = parse_award_criterion_number_threshold(xml_content)

    assert result is not None
    assert result["tender"]["lots"][0]["id"] == "LOT-002"
    assert (
        result["tender"]["lots"][0]["awardCriteria"]["criteria"][0]["numbers"][0][
            "threshold"
        ]
        == "minimumScore"
    )


def test_parse_award_criterion_number_threshold_invalid_code():
    xml_content = create_xml_with_award_criterion("LOT-003", "invalid-code")
    result = parse_award_criterion_number_threshold(xml_content)

    assert result is None


def test_parse_award_criterion_number_threshold_no_data():
    xml_content = "<root></root>"
    result = parse_award_criterion_number_threshold(xml_content)

    assert result is None


def test_merge_award_criterion_number_threshold():
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

    merge_award_criterion_number_threshold(existing_release, new_data)

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


def test_merge_award_criterion_number_threshold_new_lot():
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

    merge_award_criterion_number_threshold(existing_release, new_data)

    assert len(existing_release["tender"]["lots"]) == 1
    assert existing_release["tender"]["lots"][0]["id"] == "LOT-001"
    assert (
        existing_release["tender"]["lots"][0]["awardCriteria"]["criteria"][0][
            "numbers"
        ][0]["threshold"]
        == "minimumScore"
    )


def test_merge_award_criterion_number_threshold_no_data():
    existing_release = {"tender": {"lots": []}}
    merge_award_criterion_number_threshold(existing_release, None)
    assert existing_release == {"tender": {"lots": []}}
