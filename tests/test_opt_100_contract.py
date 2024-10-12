# tests/test_opt_100_contract.py

from ted_and_doffin_to_ocds.converters.opt_100_contract import (
    parse_framework_notice_identifier,
    merge_framework_notice_identifier,
)


def test_parse_framework_notice_identifier():
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
          xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1">
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


def test_merge_framework_notice_identifier():
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
