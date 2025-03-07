# tests/test_bt_5423_LotsGroup.py

from src.ted_and_doffin_to_ocds.converters.eforms.bt_5423_lotsgroup import (
    merge_award_criterion_number_threshold_lotsgroup,
    parse_award_criterion_number_threshold_lotsgroup,
)


def create_xml_with_award_criterion_lotsgroup(group_id, threshold_code) -> str:
    return f"""
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
          xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
          xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="LotsGroup">{group_id}</cbc:ID>
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


def test_parse_award_criterion_number_threshold_lotsgroup_max_pass() -> None:
    xml_content = create_xml_with_award_criterion_lotsgroup("GLO-001", "max-pass")
    result = parse_award_criterion_number_threshold_lotsgroup(xml_content)

    assert result is not None
    assert result["tender"]["lotGroups"][0]["id"] == "GLO-001"
    assert (
        result["tender"]["lotGroups"][0]["awardCriteria"]["criteria"][0]["numbers"][0][
            "threshold"
        ]
        == "maximumBids"
    )


def test_parse_award_criterion_number_threshold_lotsgroup_min_score() -> None:
    xml_content = create_xml_with_award_criterion_lotsgroup("GLO-002", "min-score")
    result = parse_award_criterion_number_threshold_lotsgroup(xml_content)

    assert result is not None
    assert result["tender"]["lotGroups"][0]["id"] == "GLO-002"
    assert (
        result["tender"]["lotGroups"][0]["awardCriteria"]["criteria"][0]["numbers"][0][
            "threshold"
        ]
        == "minimumScore"
    )


def test_parse_award_criterion_number_threshold_lotsgroup_invalid_code() -> None:
    xml_content = create_xml_with_award_criterion_lotsgroup("GLO-003", "invalid-code")
    result = parse_award_criterion_number_threshold_lotsgroup(xml_content)

    assert result is None


def test_parse_award_criterion_number_threshold_lotsgroup_no_data() -> None:
    xml_content = "<root></root>"
    result = parse_award_criterion_number_threshold_lotsgroup(xml_content)

    assert result is None


def test_merge_award_criterion_number_threshold_lotsgroup() -> None:
    existing_release = {
        "tender": {
            "lotGroups": [
                {
                    "id": "GLO-001",
                    "awardCriteria": {"criteria": [{"id": "AC-1", "numbers": []}]},
                },
            ],
        },
    }

    new_data = {
        "tender": {
            "lotGroups": [
                {
                    "id": "GLO-001",
                    "awardCriteria": {
                        "criteria": [{"numbers": [{"threshold": "maximumBids"}]}],
                    },
                },
            ],
        },
    }

    merge_award_criterion_number_threshold_lotsgroup(existing_release, new_data)

    assert len(existing_release["tender"]["lotGroups"]) == 1
    assert (
        len(existing_release["tender"]["lotGroups"][0]["awardCriteria"]["criteria"])
        == 1
    )
    assert (
        len(
            existing_release["tender"]["lotGroups"][0]["awardCriteria"]["criteria"][0][
                "numbers"
            ],
        )
        == 1
    )
    assert (
        existing_release["tender"]["lotGroups"][0]["awardCriteria"]["criteria"][0][
            "numbers"
        ][0]["threshold"]
        == "maximumBids"
    )


def test_merge_award_criterion_number_threshold_lotsgroup_new_group() -> None:
    existing_release = {"tender": {"lotGroups": []}}

    new_data = {
        "tender": {
            "lotGroups": [
                {
                    "id": "GLO-001",
                    "awardCriteria": {
                        "criteria": [{"numbers": [{"threshold": "minimumScore"}]}],
                    },
                },
            ],
        },
    }

    merge_award_criterion_number_threshold_lotsgroup(existing_release, new_data)

    assert len(existing_release["tender"]["lotGroups"]) == 1
    assert existing_release["tender"]["lotGroups"][0]["id"] == "GLO-001"
    assert (
        existing_release["tender"]["lotGroups"][0]["awardCriteria"]["criteria"][0][
            "numbers"
        ][0]["threshold"]
        == "minimumScore"
    )


def test_merge_award_criterion_number_threshold_lotsgroup_no_data() -> None:
    existing_release = {"tender": {"lotGroups": []}}
    merge_award_criterion_number_threshold_lotsgroup(existing_release, None)
    assert existing_release == {"tender": {"lotGroups": []}}
