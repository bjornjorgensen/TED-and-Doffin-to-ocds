# tests/test_BT_77_Lot.py

import pytest
from lxml import etree
from converters.BT_77_Lot import parse_financial_terms, merge_financial_terms
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main


def test_parse_financial_terms():
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:TenderingTerms>
                <cac:PaymentTerms>
                    <cbc:Note languageID="ENG">Any payment ...</cbc:Note>
                </cac:PaymentTerms>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </root>
    """

    result = parse_financial_terms(xml_content)

    assert result is not None
    assert "tender" in result
    assert "lots" in result["tender"]
    assert len(result["tender"]["lots"]) == 1
    assert result["tender"]["lots"][0]["id"] == "LOT-0001"
    assert (
        result["tender"]["lots"][0]["contractTerms"]["financialTerms"]
        == "Any payment ..."
    )


def test_merge_financial_terms():
    release_json = {"tender": {"lots": [{"id": "LOT-0001", "title": "Existing Lot"}]}}

    financial_terms_data = {
        "tender": {
            "lots": [
                {
                    "id": "LOT-0001",
                    "contractTerms": {"financialTerms": "Any payment ..."},
                }
            ]
        }
    }

    merge_financial_terms(release_json, financial_terms_data)

    assert "contractTerms" in release_json["tender"]["lots"][0]
    assert (
        release_json["tender"]["lots"][0]["contractTerms"]["financialTerms"]
        == "Any payment ..."
    )


def test_bt_77_lot_financial_terms_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:TenderingTerms>
                <cac:PaymentTerms>
                    <cbc:Note languageID="ENG">Any payment for LOT-0001 ...</cbc:Note>
                </cac:PaymentTerms>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0002</cbc:ID>
            <cac:TenderingTerms>
                <cac:PaymentTerms>
                    <cbc:Note languageID="ENG">Financial terms for LOT-0002 ...</cbc:Note>
                </cac:PaymentTerms>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0003</cbc:ID>
            <cac:TenderingTerms>
                <cac:PaymentTerms>
                    <cbc:Note languageID="FRA">Conditions de paiement pour LOT-0003 ...</cbc:Note>
                </cac:PaymentTerms>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </root>
    """
    xml_file = tmp_path / "test_input_financial_terms.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open("output.json", "r") as f:
        result = json.load(f)

    assert "tender" in result
    assert "lots" in result["tender"]

    lots_with_financial_terms = [
        lot
        for lot in result["tender"]["lots"]
        if "contractTerms" in lot and "financialTerms" in lot["contractTerms"]
    ]
    assert len(lots_with_financial_terms) == 3

    lot_1 = next(
        (lot for lot in lots_with_financial_terms if lot["id"] == "LOT-0001"), None
    )
    assert lot_1 is not None
    assert lot_1["contractTerms"]["financialTerms"] == "Any payment for LOT-0001 ..."

    lot_2 = next(
        (lot for lot in lots_with_financial_terms if lot["id"] == "LOT-0002"), None
    )
    assert lot_2 is not None
    assert (
        lot_2["contractTerms"]["financialTerms"] == "Financial terms for LOT-0002 ..."
    )

    lot_3 = next(
        (lot for lot in lots_with_financial_terms if lot["id"] == "LOT-0003"), None
    )
    assert lot_3 is not None
    assert (
        lot_3["contractTerms"]["financialTerms"]
        == "Conditions de paiement pour LOT-0003 ..."
    )


if __name__ == "__main__":
    pytest.main()
