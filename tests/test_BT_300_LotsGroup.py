# tests/test_BT_300_LotsGroup.py

import pytest
from converters.BT_300_LotsGroup import (
    parse_lotsgroup_additional_info,
    merge_lotsgroup_additional_info,
)


def test_parse_lotsgroup_additional_info():
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="LotsGroup">GLO-0001</cbc:ID>
            <cac:ProcurementProject>
                <cbc:Note languageID="ENG">For the current procedure ...</cbc:Note>
            </cac:ProcurementProject>
        </cac:ProcurementProjectLot>
    </root>
    """
    result = parse_lotsgroup_additional_info(xml_content)
    assert result == {
        "GLO-0001": [{"text": "For the current procedure ...", "language": "ENG"}]
    }


def test_merge_lotsgroup_additional_info():
    release_json = {"tender": {"lotGroups": [{"id": "GLO-0001"}]}}
    lotsgroup_additional_info = {
        "GLO-0001": [{"text": "For the current procedure ...", "language": "ENG"}]
    }
    merge_lotsgroup_additional_info(release_json, lotsgroup_additional_info)
    assert (
        release_json["tender"]["lotGroups"][0]["description"]
        == "For the current procedure ..."
    )


def test_merge_lotsgroup_additional_info_existing_description():
    release_json = {
        "tender": {
            "lotGroups": [{"id": "GLO-0001", "description": "Existing description."}]
        }
    }
    lotsgroup_additional_info = {
        "GLO-0001": [{"text": "Additional info.", "language": "ENG"}]
    }
    merge_lotsgroup_additional_info(release_json, lotsgroup_additional_info)
    assert (
        release_json["tender"]["lotGroups"][0]["description"]
        == "Existing description. Additional info."
    )


if __name__ == "__main__":
    pytest.main()
