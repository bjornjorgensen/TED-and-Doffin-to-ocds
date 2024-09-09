# tests/test_BT_54_Lot.py

import pytest
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main
from converters.BT_54_Lot import parse_options_description, merge_options_description


def test_parse_options_description():
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:ProcurementProject>
                <cac:ContractExtension>
                    <cbc:OptionsDescription>The buyer reserves the right to ...</cbc:OptionsDescription>
                </cac:ContractExtension>
            </cac:ProcurementProject>
        </cac:ProcurementProjectLot>
    </root>
    """

    result = parse_options_description(xml_content)

    assert result is not None
    assert "tender" in result
    assert "lots" in result["tender"]
    assert len(result["tender"]["lots"]) == 1

    lot = result["tender"]["lots"][0]
    assert lot["id"] == "LOT-0001"
    assert "options" in lot
    assert "description" in lot["options"]
    assert lot["options"]["description"] == "The buyer reserves the right to ..."


def test_merge_options_description():
    release_json = {"tender": {"lots": [{"id": "LOT-0001", "title": "Existing Lot"}]}}

    options_description_data = {
        "tender": {
            "lots": [
                {
                    "id": "LOT-0001",
                    "options": {"description": "The buyer reserves the right to ..."},
                },
                {
                    "id": "LOT-0002",
                    "options": {"description": "Another option description"},
                },
            ]
        }
    }

    merge_options_description(release_json, options_description_data)

    assert len(release_json["tender"]["lots"]) == 2

    lot1 = release_json["tender"]["lots"][0]
    assert lot1["id"] == "LOT-0001"
    assert "title" in lot1
    assert "options" in lot1
    assert lot1["options"]["description"] == "The buyer reserves the right to ..."

    lot2 = release_json["tender"]["lots"][1]
    assert lot2["id"] == "LOT-0002"
    assert "options" in lot2
    assert lot2["options"]["description"] == "Another option description"


def test_bt_54_lot_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:ProcurementProject>
                <cac:ContractExtension>
                    <cbc:OptionsDescription>The buyer reserves the right to ...</cbc:OptionsDescription>
                </cac:ContractExtension>
            </cac:ProcurementProject>
        </cac:ProcurementProjectLot>
    </root>
    """
    xml_file = tmp_path / "test_input_bt_54_lot.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open("output.json") as f:
        result = json.load(f)

    assert "tender" in result
    assert "lots" in result["tender"]
    assert len(result["tender"]["lots"]) == 1

    lot = result["tender"]["lots"][0]
    assert lot["id"] == "LOT-0001"
    assert "options" in lot
    assert "description" in lot["options"]
    assert lot["options"]["description"] == "The buyer reserves the right to ..."


if __name__ == "__main__":
    pytest.main()
