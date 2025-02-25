# tests/test_bt_04_procedure.py

from src.ted_and_doffin_to_ocds.converters.eforms.bt_04_procedure import (
    merge_procedure_identifier,
    parse_procedure_identifier,
)


def test_parse_procedure_identifier() -> None:
    xml_content = """
    <root xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cbc:ContractFolderID>1e86a664-ae3c-41eb-8529-0242ac130003</cbc:ContractFolderID>
    </root>
    """
    result = parse_procedure_identifier(xml_content)
    assert result == {"tender": {"id": "1e86a664-ae3c-41eb-8529-0242ac130003"}}


def test_merge_procedure_identifier() -> None:
    release_json = {"tender": {"title": "Some tender title"}}
    procedure_identifier_data = {
        "tender": {"id": "1e86a664-ae3c-41eb-8529-0242ac130003"},
    }
    merge_procedure_identifier(release_json, procedure_identifier_data)
    assert release_json == {
        "tender": {
            "title": "Some tender title",
            "id": "1e86a664-ae3c-41eb-8529-0242ac130003",
        },
    }


def test_parse_procedure_identifier_not_found() -> None:
    xml_content = """
    <root xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cbc:SomeOtherElement>SomeValue</cbc:SomeOtherElement>
    </root>
    """
    result = parse_procedure_identifier(xml_content)
    assert result is None


def test_merge_procedure_identifier_empty_data() -> None:
    release_json = {"tender": {"title": "Some tender title"}}
    merge_procedure_identifier(release_json, None)
    assert release_json == {"tender": {"title": "Some tender title"}}
