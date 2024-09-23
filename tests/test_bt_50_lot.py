# tests/test_bt_50_Lot.py

import pytest
from ted_and_doffin_to_ocds.converters.bt_50_lot import (
    parse_minimum_candidates,
    merge_minimum_candidates,
)


def test_parse_minimum_candidates():
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

    assert result is not None
    assert "tender" in result
    assert "lots" in result["tender"]
    assert len(result["tender"]["lots"]) == 1

    lot = result["tender"]["lots"][0]
    assert lot["id"] == "LOT-0001"
    assert "secondStage" in lot
    assert "minimumCandidates" in lot["secondStage"]
    assert lot["secondStage"]["minimumCandidates"] == 3


def test_merge_minimum_candidates():
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


if __name__ == "__main__":
    pytest.main()
