# tests/test_bt_774_Lot.py
from pathlib import Path
import pytest
from ted_and_doffin_to_ocds.converters.bt_774_lot import (
    parse_green_procurement,
    merge_green_procurement,
    ENVIRONMENTAL_IMPACT_MAPPING,
)
import json
import sys

# Add the parent directory to sys.path to import main
sys.path.append(str(Path(__file__).parent.parent))
from src.ted_and_doffin_to_ocds.main import main


def test_parse_green_procurement():
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:ProcurementProject>
                <cac:ProcurementAdditionalType>
                    <cbc:ProcurementTypeCode listName="environmental-impact">circ-econ</cbc:ProcurementTypeCode>
                </cac:ProcurementAdditionalType>
            </cac:ProcurementProject>
        </cac:ProcurementProjectLot>
    </root>
    """

    result = parse_green_procurement(xml_content)

    assert result is not None
    assert "tender" in result
    assert "lots" in result["tender"]
    assert len(result["tender"]["lots"]) == 1
    assert result["tender"]["lots"][0]["id"] == "LOT-0001"
    assert result["tender"]["lots"][0]["hasSustainability"] is True
    assert len(result["tender"]["lots"][0]["sustainability"]) == 1
    assert (
        result["tender"]["lots"][0]["sustainability"][0]["goal"]
        == ENVIRONMENTAL_IMPACT_MAPPING["circ-econ"]
    )


def test_merge_green_procurement():
    release_json = {"tender": {"lots": [{"id": "LOT-0001", "title": "Existing Lot"}]}}

    green_procurement_data = {
        "tender": {
            "lots": [
                {
                    "id": "LOT-0001",
                    "hasSustainability": True,
                    "sustainability": [{"goal": "environmental.circularEconomy"}],
                },
            ],
        },
    }

    merge_green_procurement(release_json, green_procurement_data)

    assert "hasSustainability" in release_json["tender"]["lots"][0]
    assert release_json["tender"]["lots"][0]["hasSustainability"] is True
    assert "sustainability" in release_json["tender"]["lots"][0]
    assert len(release_json["tender"]["lots"][0]["sustainability"]) == 1
    assert (
        release_json["tender"]["lots"][0]["sustainability"][0]["goal"]
        == "environmental.circularEconomy"
    )


def test_bt_774_lot_green_procurement_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:ProcurementProject>
                <cac:ProcurementAdditionalType>
                    <cbc:ProcurementTypeCode listName="environmental-impact">circ-econ</cbc:ProcurementTypeCode>
                </cac:ProcurementAdditionalType>
            </cac:ProcurementProject>
        </cac:ProcurementProjectLot>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0002</cbc:ID>
            <cac:ProcurementProject>
                <cac:ProcurementAdditionalType>
                    <cbc:ProcurementTypeCode listName="environmental-impact">biodiv-eco</cbc:ProcurementTypeCode>
                </cac:ProcurementAdditionalType>
            </cac:ProcurementProject>
        </cac:ProcurementProjectLot>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0003</cbc:ID>
            <cac:ProcurementProject>
                <cac:ProcurementAdditionalType>
                    <cbc:ProcurementTypeCode listName="other-type">not-environmental</cbc:ProcurementTypeCode>
                </cac:ProcurementAdditionalType>
            </cac:ProcurementProject>
        </cac:ProcurementProjectLot>
    </root>
    """
    xml_file = tmp_path / "test_input_green_procurement.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with Path("output.json").open() as f:
        result = json.load(f)

    assert "tender" in result
    assert "lots" in result["tender"]

    green_lots = [lot for lot in result["tender"]["lots"] if "sustainability" in lot]
    assert len(green_lots) == 2

    lot_1 = next((lot for lot in green_lots if lot["id"] == "LOT-0001"), None)
    assert lot_1 is not None
    assert lot_1["hasSustainability"] is True
    assert len(lot_1["sustainability"]) == 1
    assert (
        lot_1["sustainability"][0]["goal"] == ENVIRONMENTAL_IMPACT_MAPPING["circ-econ"]
    )

    lot_2 = next((lot for lot in green_lots if lot["id"] == "LOT-0002"), None)
    assert lot_2 is not None
    assert lot_2["hasSustainability"] is True
    assert len(lot_2["sustainability"]) == 1
    assert (
        lot_2["sustainability"][0]["goal"] == ENVIRONMENTAL_IMPACT_MAPPING["biodiv-eco"]
    )

    lot_3 = next(
        (lot for lot in result["tender"]["lots"] if lot["id"] == "LOT-0003"),
        None,
    )
    assert lot_3 is not None
    assert "sustainability" not in lot_3


if __name__ == "__main__":
    pytest.main()
