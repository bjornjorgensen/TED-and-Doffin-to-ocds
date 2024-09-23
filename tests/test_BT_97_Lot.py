# tests/test_BT_97_Lot.py

import pytest
from ted_and_doffin_to_ocds.converters.BT_97_Lot import (
    parse_submission_language,
    merge_submission_language,
)
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.ted_and_doffin_to_ocds.main import main


def test_parse_submission_language():
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:TenderingTerms>
                <cac:Language>
                    <cbc:ID>FRA</cbc:ID>
                </cac:Language>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </root>
    """

    result = parse_submission_language(xml_content)

    assert result is not None
    assert "tender" in result
    assert "lots" in result["tender"]
    assert len(result["tender"]["lots"]) == 1
    assert result["tender"]["lots"][0]["id"] == "LOT-0001"
    assert result["tender"]["lots"][0]["submissionTerms"]["languages"] == ["fr"]


def test_merge_submission_language():
    release_json = {"tender": {"lots": [{"id": "LOT-0001", "title": "Existing Lot"}]}}

    submission_language_data = {
        "tender": {
            "lots": [{"id": "LOT-0001", "submissionTerms": {"languages": ["fr"]}}],
        },
    }

    merge_submission_language(release_json, submission_language_data)

    assert "submissionTerms" in release_json["tender"]["lots"][0]
    assert "languages" in release_json["tender"]["lots"][0]["submissionTerms"]
    assert release_json["tender"]["lots"][0]["submissionTerms"]["languages"] == ["fr"]


def test_bt_97_lot_submission_language_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:TenderingTerms>
                <cac:Language>
                    <cbc:ID>FRA</cbc:ID>
                </cac:Language>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0002</cbc:ID>
            <cac:TenderingTerms>
                <cac:Language>
                    <cbc:ID>ENG</cbc:ID>
                </cac:Language>
                <cac:Language>
                    <cbc:ID>DEU</cbc:ID>
                </cac:Language>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </root>
    """
    xml_file = tmp_path / "test_input_submission_language.xml"
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
    assert lot_1["submissionTerms"]["languages"] == ["fr"]

    lot_2 = next(
        (lot for lot in result["tender"]["lots"] if lot["id"] == "LOT-0002"),
        None,
    )
    assert lot_2 is not None
    assert set(lot_2["submissionTerms"]["languages"]) == {"en", "de"}


if __name__ == "__main__":
    pytest.main()
