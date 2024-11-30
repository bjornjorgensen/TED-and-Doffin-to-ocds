# tests/test_opt_322_lotresult.py

from ted_and_doffin_to_ocds.converters.opt_322_lotresult import (
    merge_lotresult_technical_identifier,
    parse_lotresult_technical_identifier,
)


def test_parse_lotresult_technical_identifier() -> None:
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
          xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1">
        <efac:NoticeResult>
            <efac:LotResult>
                <cbc:ID schemeName="result">RES-0002</cbc:ID>
            </efac:LotResult>
        </efac:NoticeResult>
    </root>
    """
    result = parse_lotresult_technical_identifier(xml_content)
    assert result == {"awards": [{"id": "RES-0002"}]}


def test_merge_lotresult_technical_identifier() -> None:
    release_json = {"awards": [{"id": "RES-0001", "title": "Existing Award"}]}
    lotresult_technical_identifier_data = {"awards": [{"id": "RES-0002"}]}
    merge_lotresult_technical_identifier(
        release_json, lotresult_technical_identifier_data
    )
    assert release_json == {
        "awards": [{"id": "RES-0001", "title": "Existing Award"}, {"id": "RES-0002"}]
    }


def test_merge_lotresult_technical_identifier_existing_award() -> None:
    release_json = {"awards": [{"id": "RES-0002", "title": "Existing Award"}]}
    lotresult_technical_identifier_data = {"awards": [{"id": "RES-0002"}]}
    merge_lotresult_technical_identifier(
        release_json, lotresult_technical_identifier_data
    )
    assert release_json == {"awards": [{"id": "RES-0002", "title": "Existing Award"}]}


def test_merge_lotresult_technical_identifier_no_data() -> None:
    release_json = {"awards": [{"id": "RES-0001", "title": "Existing Award"}]}
    merge_lotresult_technical_identifier(release_json, None)
    assert release_json == {"awards": [{"id": "RES-0001", "title": "Existing Award"}]}
