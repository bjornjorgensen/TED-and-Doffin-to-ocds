# tests/test_bt_99_Lot.py

import pytest
from ted_and_doffin_to_ocds.converters.bt_99_lot import (
    parse_review_deadline_description,
    merge_review_deadline_description,
)
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.ted_and_doffin_to_ocds.main import main


def test_parse_review_deadline_description():
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:TenderingTerms>
                <cac:AppealTerms>
                    <cac:PresentationPeriod>
                        <cbc:Description>Any review request shall be submitted ...</cbc:Description>
                    </cac:PresentationPeriod>
                </cac:AppealTerms>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </root>
    """

    result = parse_review_deadline_description(xml_content)

    assert result is not None
    assert "tender" in result
    assert "lots" in result["tender"]
    assert len(result["tender"]["lots"]) == 1
    assert result["tender"]["lots"][0]["id"] == "LOT-0001"
    assert (
        result["tender"]["lots"][0]["reviewDetails"]
        == "Any review request shall be submitted ..."
    )


def test_merge_review_deadline_description():
    release_json = {"tender": {"lots": [{"id": "LOT-0001", "title": "Existing Lot"}]}}

    review_deadline_description_data = {
        "tender": {
            "lots": [
                {
                    "id": "LOT-0001",
                    "reviewDetails": "Any review request shall be submitted ...",
                },
            ],
        },
    }

    merge_review_deadline_description(release_json, review_deadline_description_data)

    assert "reviewDetails" in release_json["tender"]["lots"][0]
    assert (
        release_json["tender"]["lots"][0]["reviewDetails"]
        == "Any review request shall be submitted ..."
    )


def test_bt_99_lot_review_deadline_description_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:TenderingTerms>
                <cac:AppealTerms>
                    <cac:PresentationPeriod>
                        <cbc:Description>Any review request shall be submitted ...</cbc:Description>
                    </cac:PresentationPeriod>
                </cac:AppealTerms>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0002</cbc:ID>
            <cac:TenderingTerms>
                <cac:AppealTerms>
                    <cac:PresentationPeriod>
                        <cbc:Description>Review requests must be filed within 10 days...</cbc:Description>
                    </cac:PresentationPeriod>
                </cac:AppealTerms>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </root>
    """
    xml_file = tmp_path / "test_input_review_deadline_description.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open("output.json") as f:
        result = json.load(f)

    assert "tender" in result
    assert "lots" in result["tender"]
    assert len(result["tender"]["lots"]) == 2

    lot_1 = next(
        (lot for lot in result["tender"]["lots"] if lot["id"] == "LOT-0001"),
        None,
    )
    assert lot_1 is not None
    assert lot_1["reviewDetails"] == "Any review request shall be submitted ..."

    lot_2 = next(
        (lot for lot in result["tender"]["lots"] if lot["id"] == "LOT-0002"),
        None,
    )
    assert lot_2 is not None
    assert lot_2["reviewDetails"] == "Review requests must be filed within 10 days..."


if __name__ == "__main__":
    pytest.main()
