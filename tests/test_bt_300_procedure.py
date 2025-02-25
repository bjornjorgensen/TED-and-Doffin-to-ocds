# tests/test_bt_300_procedure.py

import pytest

from src.ted_and_doffin_to_ocds.converters.eforms.bt_300_procedure import (
    merge_procedure_additional_info,
    parse_procedure_additional_info,
)


def test_parse_procedure_additional_info() -> None:
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProject>
            <cbc:Note languageID="ENG">For the current procedure ...</cbc:Note>
        </cac:ProcurementProject>
    </root>
    """
    result = parse_procedure_additional_info(xml_content)
    assert result == [{"text": "For the current procedure ...", "language": "ENG"}]


def test_merge_procedure_additional_info() -> None:
    release_json = {}
    procedure_additional_info = [
        {"text": "For the current procedure ...", "language": "ENG"},
    ]
    merge_procedure_additional_info(release_json, procedure_additional_info)
    assert release_json["description"] == "For the current procedure ..."


def test_merge_procedure_additional_info_existing_description() -> None:
    release_json = {"description": "Existing description."}
    procedure_additional_info = [{"text": "Additional info.", "language": "ENG"}]
    merge_procedure_additional_info(release_json, procedure_additional_info)
    assert release_json["description"] == "Existing description. Additional info."


def test_merge_multiple_procedure_additional_info() -> None:
    release_json = {}
    procedure_additional_info = [
        {"text": "First part of info.", "language": "ENG"},
        {"text": "Second part of info.", "language": "FRA"},
    ]
    merge_procedure_additional_info(release_json, procedure_additional_info)
    assert release_json["description"] == "First part of info. Second part of info."


if __name__ == "__main__":
    pytest.main()
