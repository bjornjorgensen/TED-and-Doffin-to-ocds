# tests/test_BT_300_Lot.py

import pytest
from ted_and_doffin_to_ocds.converters.BT_300_Lot import (
    parse_lot_additional_info,
    merge_lot_additional_info,
)


def test_parse_lot_additional_info():
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:ProcurementProject>
                <cbc:Note languageID="ENG">For the current procedure ...</cbc:Note>
            </cac:ProcurementProject>
        </cac:ProcurementProjectLot>
    </root>
    """
    result = parse_lot_additional_info(xml_content)
    assert result == {
        "LOT-0001": [{"text": "For the current procedure ...", "language": "ENG"}],
    }


def test_merge_lot_additional_info():
    release_json = {"tender": {"lots": [{"id": "LOT-0001"}]}}
    lot_additional_info = {
        "LOT-0001": [{"text": "For the current procedure ...", "language": "ENG"}],
    }
    merge_lot_additional_info(release_json, lot_additional_info)
    assert (
        release_json["tender"]["lots"][0]["description"]
        == "For the current procedure ..."
    )


def test_merge_lot_additional_info_existing_description():
    release_json = {
        "tender": {
            "lots": [{"id": "LOT-0001", "description": "Existing description."}]
        },
    }
    lot_additional_info = {
        "LOT-0001": [{"text": "Additional info.", "language": "ENG"}],
    }
    merge_lot_additional_info(release_json, lot_additional_info)
    assert (
        release_json["tender"]["lots"][0]["description"]
        == "Existing description. Additional info."
    )


if __name__ == "__main__":
    pytest.main()
