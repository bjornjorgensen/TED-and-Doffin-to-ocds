# tests/test_bt_94_Lot.py
from pathlib import Path
import pytest
from ted_and_doffin_to_ocds.converters.bt_94_lot import (
    parse_recurrence,
    merge_recurrence,
)
import json
import sys

# Add the parent directory to sys.path to import main
sys.path.append(str(Path(__file__).parent.parent))
from src.ted_and_doffin_to_ocds.main import main


def test_parse_recurrence():
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:TenderingTerms>
                <cbc:RecurringProcurementIndicator>true</cbc:RecurringProcurementIndicator>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </root>
    """

    result = parse_recurrence(xml_content)

    assert result is not None
    assert "tender" in result
    assert "lots" in result["tender"]
    assert len(result["tender"]["lots"]) == 1
    assert result["tender"]["lots"][0]["id"] == "LOT-0001"
    assert result["tender"]["lots"][0]["hasRecurrence"] is True


def test_merge_recurrence():
    release_json = {"tender": {"lots": [{"id": "LOT-0001", "title": "Existing Lot"}]}}

    recurrence_data = {"tender": {"lots": [{"id": "LOT-0001", "hasRecurrence": True}]}}

    merge_recurrence(release_json, recurrence_data)

    assert "hasRecurrence" in release_json["tender"]["lots"][0]
    assert release_json["tender"]["lots"][0]["hasRecurrence"] is True


def test_bt_94_lot_recurrence_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:TenderingTerms>
                <cbc:RecurringProcurementIndicator>true</cbc:RecurringProcurementIndicator>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0002</cbc:ID>
            <cac:TenderingTerms>
                <cbc:RecurringProcurementIndicator>false</cbc:RecurringProcurementIndicator>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </root>
    """
    xml_file = tmp_path / "test_input_recurrence.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with Path("output.json").open() as f:
        result = json.load(f)

    assert "tender" in result
    assert "lots" in result["tender"]
    assert len(result["tender"]["lots"]) == 2

    lot_1 = next(
        (lot for lot in result["tender"]["lots"] if lot["id"] == "LOT-0001"),
        None,
    )
    assert lot_1 is not None
    assert lot_1["hasRecurrence"] is True

    lot_2 = next(
        (lot for lot in result["tender"]["lots"] if lot["id"] == "LOT-0002"),
        None,
    )
    assert lot_2 is not None
    assert lot_2["hasRecurrence"] is False


if __name__ == "__main__":
    pytest.main()