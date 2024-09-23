# tests/test_BT_300_Part.py

import pytest
from ted_and_doffin_to_ocds.converters.BT_300_Part import (
    parse_part_additional_info,
    merge_part_additional_info,
)


def test_parse_part_additional_info():
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Part">PART-0001</cbc:ID>
            <cac:ProcurementProject>
                <cbc:Note languageID="ENG">For the current procedure ...</cbc:Note>
            </cac:ProcurementProject>
        </cac:ProcurementProjectLot>
    </root>
    """
    result = parse_part_additional_info(xml_content)
    assert result == [{"text": "For the current procedure ...", "language": "ENG"}]


def test_merge_part_additional_info():
    release_json = {}
    part_additional_info = [
        {"text": "For the current procedure ...", "language": "ENG"},
    ]
    merge_part_additional_info(release_json, part_additional_info)
    assert release_json["description"] == "For the current procedure ..."


def test_merge_part_additional_info_existing_description():
    release_json = {"description": "Existing description."}
    part_additional_info = [{"text": "Additional info.", "language": "ENG"}]
    merge_part_additional_info(release_json, part_additional_info)
    assert release_json["description"] == "Existing description. Additional info."


def test_merge_multiple_part_additional_info():
    release_json = {}
    part_additional_info = [
        {"text": "First part of info.", "language": "ENG"},
        {"text": "Second part of info.", "language": "FRA"},
    ]
    merge_part_additional_info(release_json, part_additional_info)
    assert release_json["description"] == "First part of info. Second part of info."


if __name__ == "__main__":
    pytest.main()
