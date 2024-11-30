# tests/test_opt_201_organization_touchpoint.py

from ted_and_doffin_to_ocds.converters.opt_201_organization_touchpoint import (
    merge_touchpoint_technical_identifier,
    parse_touchpoint_technical_identifier,
)


def test_parse_touchpoint_technical_identifier() -> None:
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
          xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1">
        <ext:UBLExtensions>
            <ext:UBLExtension>
                <ext:ExtensionContent>
                    <efext:EformsExtension>
                        <efac:Organizations>
                            <efac:Organization>
                                <efac:TouchPoint>
                                    <cac:PartyIdentification>
                                        <cbc:ID schemeName="touchpoint">TPO-0001</cbc:ID>
                                    </cac:PartyIdentification>
                                </efac:TouchPoint>
                            </efac:Organization>
                        </efac:Organizations>
                    </efext:EformsExtension>
                </ext:ExtensionContent>
            </ext:UBLExtension>
        </ext:UBLExtensions>
    </root>
    """

    result = parse_touchpoint_technical_identifier(xml_content)

    assert result is not None
    assert "parties" in result
    assert len(result["parties"]) == 1
    assert result["parties"][0]["id"] == "TPO-0001"


def test_merge_touchpoint_technical_identifier() -> None:
    release_json = {"parties": []}
    touchpoint_data = {"parties": [{"id": "TPO-0001"}]}

    merge_touchpoint_technical_identifier(release_json, touchpoint_data)

    assert "parties" in release_json
    assert len(release_json["parties"]) == 1
    assert release_json["parties"][0]["id"] == "TPO-0001"


def test_merge_touchpoint_technical_identifier_existing_party() -> None:
    release_json = {"parties": [{"id": "TPO-0001", "name": "Existing TouchPoint"}]}
    touchpoint_data = {"parties": [{"id": "TPO-0001"}, {"id": "TPO-0002"}]}

    merge_touchpoint_technical_identifier(release_json, touchpoint_data)

    assert len(release_json["parties"]) == 2
    assert release_json["parties"][0]["id"] == "TPO-0001"
    assert release_json["parties"][0]["name"] == "Existing TouchPoint"
    assert release_json["parties"][1]["id"] == "TPO-0002"
