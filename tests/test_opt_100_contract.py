# tests/test_opt_100_contract.py

from src.ted_and_doffin_to_ocds.converters.eforms.opt_100_contract import (
    merge_framework_notice_identifier,
    parse_framework_notice_identifier,
)


def test_parse_framework_notice_identifier() -> None:
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
                        <efac:NoticeResult>
                            <efac:SettledContract>
                                <cbc:ID schemeName="contract">CON-0001</cbc:ID>
                                <cac:NoticeDocumentReference>
                                    <cbc:ID schemeName="ojs-notice-id">62783-2020</cbc:ID>
                                </cac:NoticeDocumentReference>
                            </efac:SettledContract>
                            <efac:LotResult>
                                <cbc:ID schemeName="result">RES-0001</cbc:ID>
                                <efac:SettledContract>
                                    <cbc:ID schemeName="contract">CON-0001</cbc:ID>
                                </efac:SettledContract>
                            </efac:LotResult>
                        </efac:NoticeResult>
                    </efext:EformsExtension>
                </ext:ExtensionContent>
            </ext:UBLExtension>
        </ext:UBLExtensions>
    </root>
    """
    result = parse_framework_notice_identifier(xml_content)
    assert result == {
        "contracts": [
            {
                "id": "CON-0001",
                "awardID": "RES-0001",
                "relatedProcesses": [
                    {
                        "id": "1",
                        "scheme": "ojs-notice-id",
                        "identifier": "62783-2020",
                        "relationship": ["framework"],
                    }
                ],
            }
        ]
    }


def test_parse_framework_notice_identifier_bytes() -> None:
    """Test handling of bytes input."""
    xml_content = b"""
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
          xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1">
        <ext:UBLExtensions>
            <ext:UBLExtension>
                <ext:ExtensionContent>
                    <efext:EformsExtension>
                        <efac:NoticeResult>
                            <efac:SettledContract>
                                <cbc:ID schemeName="contract">CON-0002</cbc:ID>
                                <cac:NoticeDocumentReference>
                                    <cbc:ID schemeName="ojs-notice-id">12345-2020</cbc:ID>
                                </cac:NoticeDocumentReference>
                            </efac:SettledContract>
                            <efac:LotResult>
                                <cbc:ID schemeName="result">RES-0002</cbc:ID>
                                <efac:SettledContract>
                                    <cbc:ID schemeName="contract">CON-0002</cbc:ID>
                                </efac:SettledContract>
                            </efac:LotResult>
                        </efac:NoticeResult>
                    </efext:EformsExtension>
                </ext:ExtensionContent>
            </ext:UBLExtension>
        </ext:UBLExtensions>
    </root>
    """
    result = parse_framework_notice_identifier(xml_content)
    assert result == {
        "contracts": [
            {
                "id": "CON-0002",
                "awardID": "RES-0002",
                "relatedProcesses": [
                    {
                        "id": "1",
                        "scheme": "ojs-notice-id",
                        "identifier": "12345-2020",
                        "relationship": ["framework"],
                    }
                ],
            }
        ]
    }


def test_parse_framework_notice_identifier_ocds_scheme() -> None:
    """Test handling of OCDS scheme which should convert to OCID."""
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
                        <efac:NoticeResult>
                            <efac:SettledContract>
                                <cbc:ID schemeName="contract">CON-0003</cbc:ID>
                                <cac:NoticeDocumentReference>
                                    <cbc:ID schemeName="ocds">ocds-abc123-CA01</cbc:ID>
                                </cac:NoticeDocumentReference>
                            </efac:SettledContract>
                        </efac:NoticeResult>
                    </efext:EformsExtension>
                </ext:ExtensionContent>
            </ext:UBLExtension>
        </ext:UBLExtensions>
    </root>
    """
    result = parse_framework_notice_identifier(xml_content)
    assert result == {
        "contracts": [
            {
                "id": "CON-0003",
                "relatedProcesses": [
                    {
                        "id": "1",
                        "scheme": "ocid",  # Converted from "ocds"
                        "identifier": "ocds-abc123-CA01",
                        "relationship": ["framework"],
                    }
                ],
            }
        ]
    }


def test_parse_framework_notice_identifier_no_data() -> None:
    """Test handling when no framework data is found."""
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
                        <efac:NoticeResult>
                            <!-- No SettledContract elements -->
                        </efac:NoticeResult>
                    </efext:EformsExtension>
                </ext:ExtensionContent>
            </ext:UBLExtension>
        </ext:UBLExtensions>
    </root>
    """
    result = parse_framework_notice_identifier(xml_content)
    assert result is None


def test_parse_framework_notice_identifier_invalid_xml() -> None:
    """Test handling of invalid XML."""
    xml_content = "<invalid>XML Content</invalid"
    result = parse_framework_notice_identifier(xml_content)
    assert result is None


def test_merge_framework_notice_identifier() -> None:
    release_json = {"contracts": [{"id": "CON-0001", "title": "Existing Contract"}]}
    framework_notice_identifier_data = {
        "contracts": [
            {
                "id": "CON-0001",
                "awardID": "RES-0001",
                "relatedProcesses": [
                    {
                        "id": "1",
                        "scheme": "ojs-notice-id",
                        "identifier": "62783-2020",
                        "relationship": ["framework"],
                    }
                ],
            }
        ]
    }
    merge_framework_notice_identifier(release_json, framework_notice_identifier_data)
    assert release_json == {
        "contracts": [
            {
                "id": "CON-0001",
                "title": "Existing Contract",
                "awardID": "RES-0001",
                "relatedProcesses": [
                    {
                        "id": "1",
                        "scheme": "ojs-notice-id",
                        "identifier": "62783-2020",
                        "relationship": ["framework"],
                    }
                ],
            }
        ]
    }


def test_merge_framework_notice_identifier_new_contract() -> None:
    """Test merging when the contract doesn't already exist."""
    release_json = {"contracts": [{"id": "EXISTING-CON", "title": "Existing Contract"}]}
    framework_notice_identifier_data = {
        "contracts": [
            {
                "id": "NEW-CON",
                "awardID": "RES-0003",
                "relatedProcesses": [
                    {
                        "id": "1",
                        "scheme": "ojs-notice-id",
                        "identifier": "98765-2021",
                        "relationship": ["framework"],
                    }
                ],
            }
        ]
    }
    merge_framework_notice_identifier(release_json, framework_notice_identifier_data)
    assert release_json == {
        "contracts": [
            {"id": "EXISTING-CON", "title": "Existing Contract"},
            {
                "id": "NEW-CON",
                "awardID": "RES-0003",
                "relatedProcesses": [
                    {
                        "id": "1",
                        "scheme": "ojs-notice-id",
                        "identifier": "98765-2021",
                        "relationship": ["framework"],
                    }
                ],
            }
        ]
    }


def test_merge_framework_notice_identifier_none_data() -> None:
    """Test merging when framework data is None."""
    release_json = {"contracts": [{"id": "CON-0001", "title": "Existing Contract"}]}
    merge_framework_notice_identifier(release_json, None)
    # Should remain unchanged
    assert release_json == {"contracts": [{"id": "CON-0001", "title": "Existing Contract"}]}


def test_merge_framework_notice_identifier_existing_related_process() -> None:
    """Test merging when the contract already has related processes."""
    release_json = {
        "contracts": [
            {
                "id": "CON-0001", 
                "title": "Existing Contract",
                "relatedProcesses": [
                    {
                        "id": "1",
                        "scheme": "old-scheme",
                        "identifier": "old-identifier",
                        "relationship": ["old-relationship"],
                    }
                ]
            }
        ]
    }
    framework_notice_identifier_data = {
        "contracts": [
            {
                "id": "CON-0001",
                "relatedProcesses": [
                    {
                        "id": "1",
                        "scheme": "ojs-notice-id",
                        "identifier": "62783-2020",
                        "relationship": ["framework"],
                    }
                ],
            }
        ]
    }
    merge_framework_notice_identifier(release_json, framework_notice_identifier_data)
    # The existing related process should be updated
    assert release_json == {
        "contracts": [
            {
                "id": "CON-0001",
                "title": "Existing Contract",
                "relatedProcesses": [
                    {
                        "id": "1",
                        "scheme": "ojs-notice-id",
                        "identifier": "62783-2020",
                        "relationship": ["framework"],
                    }
                ],
            }
        ]
    }
