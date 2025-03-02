# tests/test_bt_50_Lot.py

import pytest

from src.ted_and_doffin_to_ocds.converters.eforms.bt_50_lot import (
    merge_minimum_candidates,
    parse_minimum_candidates,
)


def test_parse_minimum_candidates() -> None:
    """Test parsing minimum candidates from TenderingProcess path."""
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:TenderingProcess>
                <cac:EconomicOperatorShortList>
                    <cbc:MinimumQuantity>4</cbc:MinimumQuantity>
                </cac:EconomicOperatorShortList>
            </cac:TenderingProcess>
        </cac:ProcurementProjectLot>
    </root>
    """

    result = parse_minimum_candidates(xml_content)

    assert result is not None
    assert "tender" in result
    assert "lots" in result["tender"]
    assert len(result["tender"]["lots"]) == 1

    lot = result["tender"]["lots"][0]
    assert lot["id"] == "LOT-0001"
    assert "secondStage" in lot
    assert "minimumCandidates" in lot["secondStage"]
    assert lot["secondStage"]["minimumCandidates"] == 4


def test_parse_minimum_candidates_tendering_terms_path() -> None:
    """Test that minimum candidates in TenderingTerms path is ignored."""
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:TenderingTerms>
                <cac:EconomicOperatorShortList>
                    <cbc:MinimumQuantity>3</cbc:MinimumQuantity>
                </cac:EconomicOperatorShortList>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </root>
    """

    result = parse_minimum_candidates(xml_content)
    assert result is None


def test_parse_minimum_candidates_no_data() -> None:
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:TenderingTerms>
                <!-- No EconomicOperatorShortList element -->
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </root>
    """

    result = parse_minimum_candidates(xml_content)
    assert result is None


def test_parse_minimum_candidates_multiple_lots() -> None:
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:TenderingProcess>
                <cac:EconomicOperatorShortList>
                    <cbc:MinimumQuantity>3</cbc:MinimumQuantity>
                </cac:EconomicOperatorShortList>
            </cac:TenderingProcess>
        </cac:ProcurementProjectLot>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0002</cbc:ID>
            <cac:TenderingProcess>
                <cac:EconomicOperatorShortList>
                    <cbc:MinimumQuantity>5</cbc:MinimumQuantity>
                </cac:EconomicOperatorShortList>
            </cac:TenderingProcess>
        </cac:ProcurementProjectLot>
    </root>
    """

    result = parse_minimum_candidates(xml_content)

    assert result is not None
    assert "tender" in result
    assert "lots" in result["tender"]
    assert len(result["tender"]["lots"]) == 2

    assert result["tender"]["lots"][0]["id"] == "LOT-0001"
    assert result["tender"]["lots"][0]["secondStage"]["minimumCandidates"] == 3
    
    assert result["tender"]["lots"][1]["id"] == "LOT-0002"
    assert result["tender"]["lots"][1]["secondStage"]["minimumCandidates"] == 5


def test_merge_minimum_candidates() -> None:
    minimum_candidates_data = {
        "tender": {
            "lots": [{"id": "LOT-0001", "secondStage": {"minimumCandidates": 3}}],
        },
    }

    release_json = {"tender": {"lots": [{"id": "LOT-0001", "title": "Existing Lot"}]}}

    merge_minimum_candidates(release_json, minimum_candidates_data)

    assert "secondStage" in release_json["tender"]["lots"][0]
    assert "minimumCandidates" in release_json["tender"]["lots"][0]["secondStage"]
    assert release_json["tender"]["lots"][0]["secondStage"]["minimumCandidates"] == 3


def test_merge_minimum_candidates_empty_data() -> None:
    release_json = {"tender": {"lots": [{"id": "LOT-0001", "title": "Existing Lot"}]}}
    
    # Test with None input
    merge_minimum_candidates(release_json, None)
    assert "secondStage" not in release_json["tender"]["lots"][0]
    
    # Test with empty lots
    merge_minimum_candidates(release_json, {"tender": {"lots": []}})
    assert "secondStage" not in release_json["tender"]["lots"][0]


if __name__ == "__main__":
    pytest.main()
