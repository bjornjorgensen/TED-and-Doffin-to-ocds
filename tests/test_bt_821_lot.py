from ted_and_doffin_to_ocds.converters.bt_821_lot import (
    merge_selection_criteria_source,
    parse_selection_criteria_source,
)


def test_parse_selection_criteria_source_valid():
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:TenderingTerms>
                <cac:TendererQualificationRequest>
                    <cac:SpecificTendererRequirement>
                        <cbc:TendererRequirementTypeCode listName="selection-criteria-source">epo-procurement-document</cbc:TendererRequirementTypeCode>
                    </cac:SpecificTendererRequirement>
                </cac:TendererQualificationRequest>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </root>
    """
    expected = {
        "tender": {
            "lots": [
                {
                    "id": "LOT-0001",
                    "selectionCriteria": {"sources": ["epo-procurement-document"]},
                }
            ]
        }
    }
    result = parse_selection_criteria_source(xml_content)
    assert result == expected


def test_parse_selection_criteria_source_no_sources():
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0002</cbc:ID>
            <cac:TenderingTerms>
                <cac:TendererQualificationRequest>
                    <!-- No SpecificTendererRequirement -->
                </cac:TendererQualificationRequest>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </root>
    """
    result = parse_selection_criteria_source(xml_content)
    assert result is None


def test_merge_selection_criteria_source_new_lot():
    release_json = {"tender": {"lots": []}}
    selection_criteria_data = {
        "tender": {
            "lots": [
                {
                    "id": "LOT-0001",
                    "selectionCriteria": {"sources": ["epo-procurement-document"]},
                }
            ]
        }
    }
    merge_selection_criteria_source(release_json, selection_criteria_data)
    assert release_json["tender"]["lots"] == selection_criteria_data["tender"]["lots"]


def test_merge_selection_criteria_source_existing_lot():
    release_json = {
        "tender": {
            "lots": [
                {
                    "id": "LOT-0001",
                    "selectionCriteria": {"sources": ["existing-source"]},
                }
            ]
        }
    }
    selection_criteria_data = {
        "tender": {
            "lots": [
                {"id": "LOT-0001", "selectionCriteria": {"sources": ["new-source"]}}
            ]
        }
    }
    merge_selection_criteria_source(release_json, selection_criteria_data)
    assert release_json["tender"]["lots"][0]["selectionCriteria"]["sources"] == [
        "existing-source",
        "new-source",
    ]


def test_merge_selection_criteria_source_duplicate_sources():
    release_json = {
        "tender": {
            "lots": [{"id": "LOT-0001", "selectionCriteria": {"sources": ["source1"]}}]
        }
    }
    selection_criteria_data = {
        "tender": {
            "lots": [
                {
                    "id": "LOT-0001",
                    "selectionCriteria": {"sources": ["source1", "source2"]},
                }
            ]
        }
    }
    merge_selection_criteria_source(release_json, selection_criteria_data)
    assert release_json["tender"]["lots"][0]["selectionCriteria"]["sources"] == [
        "source1",
        "source2",
    ]


def test_merge_selection_criteria_source_no_data():
    release_json = {"tender": {"lots": []}}
    merge_selection_criteria_source(release_json, None)
    assert release_json["tender"]["lots"] == []
