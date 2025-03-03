# tests/test_bt_500_organization_touchpoint.py

from src.ted_and_doffin_to_ocds.converters.eforms.bt_500_organization_touchpoint import (
    merge_organization_touchpoint_name,
    parse_organization_touchpoint_name,
)


def test_parse_organization_touchpoint_name() -> None:
    xml_content = """
    <Notice xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
      xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
      xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
      xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
      xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1">
    <ext:UBLExtensions>
        <ext:UBLExtension>
            <ext:ExtensionContent>
                <efext:EformsExtension>
                    <efac:Organizations>
                        <efac:Organization>
                            <efac:Company>
                                <cac:PartyLegalEntity>
                                    <cbc:CompanyID>998298</cbc:CompanyID>
                                </cac:PartyLegalEntity>
                            </efac:Company>
                            <efac:TouchPoint>
                                <cac:PartyIdentification>
                                    <cbc:ID schemeName="touchpoint">TPO-0001</cbc:ID>
                                </cac:PartyIdentification>
                                <cac:PartyName>
                                    <cbc:Name languageID="ENG">Ministry of Education</cbc:Name>
                                </cac:PartyName>
                            </efac:TouchPoint>
                        </efac:Organization>
                    </efac:Organizations>
                </efext:EformsExtension>
            </ext:ExtensionContent>
        </ext:UBLExtension>
    </ext:UBLExtensions>
</Notice>
    """

    result = parse_organization_touchpoint_name(xml_content)
    assert result == {
        "parties": [
            {
                "id": "TPO-0001",
                "name": "Ministry of Education",
                "identifier": {"id": "998298", "scheme": "internal"},
            }
        ]
    }


def test_parse_organization_touchpoint_name_multilingual() -> None:
    xml_content = """
    <Notice xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
      xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
      xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
      xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
      xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1">
    <ext:UBLExtensions>
        <ext:UBLExtension>
            <ext:ExtensionContent>
                <efext:EformsExtension>
                    <efac:Organizations>
                        <efac:Organization>
                            <efac:Company>
                                <cac:PartyLegalEntity>
                                    <cbc:CompanyID>998298</cbc:CompanyID>
                                </cac:PartyLegalEntity>
                            </efac:Company>
                            <efac:TouchPoint>
                                <cac:PartyIdentification>
                                    <cbc:ID schemeName="touchpoint">TPO-0001</cbc:ID>
                                </cac:PartyIdentification>
                                <cac:PartyName>
                                    <cbc:Name languageID="ENG">Ministry of Education</cbc:Name>
                                    <cbc:Name languageID="NOR">Utdanningsdepartementet</cbc:Name>
                                </cac:PartyName>
                            </efac:TouchPoint>
                        </efac:Organization>
                    </efac:Organizations>
                </efext:EformsExtension>
            </ext:ExtensionContent>
        </ext:UBLExtension>
    </ext:UBLExtensions>
</Notice>
    """

    result = parse_organization_touchpoint_name(xml_content)
    assert result == {
        "parties": [
            {
                "id": "TPO-0001",
                "name": "Ministry of Education",
                "identifier": {"id": "998298", "scheme": "internal"},
            }
        ]
    }


def test_parse_organization_touchpoint_name_without_language_id() -> None:
    xml_content = """
    <Notice xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
      xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
      xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
      xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
      xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1">
        <ext:UBLExtensions>
            <ext:UBLExtension>
                <ext:ExtensionContent>
                    <efext:EformsExtension>
                        <efac:Organizations>
                            <efac:Organization>
                                <efac:Company>
                                    <cac:PartyLegalEntity>
                                        <cbc:CompanyID>998298</cbc:CompanyID>
                                    </cac:PartyLegalEntity>
                                </efac:Company>
                                <efac:TouchPoint>
                                    <cac:PartyIdentification>
                                        <cbc:ID schemeName="touchpoint">TPO-0001</cbc:ID>
                                    </cac:PartyIdentification>
                                    <cac:PartyName>
                                        <cbc:Name languageID="ENG">Ministry of Education</cbc:Name>
                                    </cac:PartyName>
                                </efac:TouchPoint>
                            </efac:Organization>
                        </efac:Organizations>
                    </efext:EformsExtension>
                </ext:ExtensionContent>
            </ext:UBLExtension>
        </ext:UBLExtensions>
    </Notice>
    """

    result = parse_organization_touchpoint_name(xml_content)
    assert result == {
        "parties": [
            {
                "id": "TPO-0001",
                "name": "Ministry of Education",
                "identifier": {"id": "998298", "scheme": "internal"},
            }
        ]
    }


def test_merge_organization_touchpoint_name() -> None:
    release_json = {
        "parties": [{"id": "TPO-0001", "address": {"streetAddress": "123 Main St"}}]
    }

    organization_touchpoint_name_data = {
        "parties": [
            {
                "id": "TPO-0001",
                "name": "Ministry of Education",
                "identifier": {"id": "998298", "scheme": "internal"},
            }
        ]
    }

    merge_organization_touchpoint_name(release_json, organization_touchpoint_name_data)

    assert release_json == {
        "parties": [
            {
                "id": "TPO-0001",
                "name": "Ministry of Education",
                "address": {"streetAddress": "123 Main St"},
                "identifier": {"id": "998298", "scheme": "internal"},
            }
        ]
    }


def test_merge_organization_touchpoint_name_new_party() -> None:
    release_json = {"parties": [{"id": "TPO-0001", "name": "Ministry of Education"}]}

    organization_touchpoint_name_data = {
        "parties": [
            {
                "id": "TPO-0002",
                "name": "Ministry of Health",
                "identifier": {"id": "998299", "scheme": "internal"},
            }
        ]
    }

    merge_organization_touchpoint_name(release_json, organization_touchpoint_name_data)

    assert release_json == {
        "parties": [
            {"id": "TPO-0001", "name": "Ministry of Education"},
            {
                "id": "TPO-0002",
                "name": "Ministry of Health",
                "identifier": {"id": "998299", "scheme": "internal"},
            },
        ]
    }


def test_merge_organization_touchpoint_name_empty_data() -> None:
    release_json = {"parties": [{"id": "TPO-0001", "name": "Ministry of Education"}]}
    merge_organization_touchpoint_name(release_json, None)
    assert release_json == {"parties": [{"id": "TPO-0001", "name": "Ministry of Education"}]}
