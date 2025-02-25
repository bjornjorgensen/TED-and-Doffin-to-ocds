# tests/test_opt_301_tenderer_subcont.py

from src.ted_and_doffin_to_ocds.converters.eforms.opt_301_tenderer_subcont import (
    merge_subcontractor,
    parse_subcontractor,
)


def test_parse_subcontractor() -> None:
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
          xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1">
        <efac:NoticeResult>
            <efac:LotTender>
                <cbc:ID schemeName="tender">TEN-0001</cbc:ID>
            </efac:LotTender>
            <efac:TenderingParty>
                <efac:SubContractor>
                    <cbc:ID schemeName="organization">ORG-0012</cbc:ID>
                </efac:SubContractor>
            </efac:TenderingParty>
        </efac:NoticeResult>
        <efac:Organizations>
            <efac:Organization>
                <efac:Company>
                    <cac:PartyIdentification>
                        <cbc:ID schemeName="organization">ORG-0012</cbc:ID>
                    </cac:PartyIdentification>
                </efac:Company>
            </efac:Organization>
        </efac:Organizations>
    </root>
    """
    result = parse_subcontractor(xml_content)
    assert result == {
        "parties": [{"id": "ORG-0012", "roles": ["subcontractor"]}],
        "bids": {
            "details": [
                {
                    "id": "TEN-0001",
                    "subcontracting": {
                        "subcontracts": [
                            {"id": "1", "subcontractor": {"id": "ORG-0012"}}
                        ]
                    },
                }
            ]
        },
    }


def test_merge_subcontractor() -> None:
    release_json = {
        "parties": [{"id": "ORG-0012", "roles": ["tenderer"]}],
        "bids": {
            "details": [{"id": "TEN-0001", "subcontracting": {"subcontracts": []}}]
        },
    }
    subcontractor_data = {
        "parties": [{"id": "ORG-0012", "roles": ["subcontractor"]}],
        "bids": {
            "details": [
                {
                    "id": "TEN-0001",
                    "subcontracting": {
                        "subcontracts": [
                            {"id": "1", "subcontractor": {"id": "ORG-0012"}}
                        ]
                    },
                }
            ]
        },
    }
    merge_subcontractor(release_json, subcontractor_data)
    assert release_json == {
        "parties": [{"id": "ORG-0012", "roles": ["tenderer", "subcontractor"]}],
        "bids": {
            "details": [
                {
                    "id": "TEN-0001",
                    "subcontracting": {
                        "subcontracts": [
                            {"id": "1", "subcontractor": {"id": "ORG-0012"}}
                        ]
                    },
                }
            ]
        },
    }


def test_merge_subcontractor_new_data() -> None:
    release_json = {
        "parties": [{"id": "ORG-0001", "roles": ["buyer"]}],
        "bids": {
            "details": [{"id": "TEN-0002", "subcontracting": {"subcontracts": []}}]
        },
    }
    subcontractor_data = {
        "parties": [{"id": "ORG-0012", "roles": ["subcontractor"]}],
        "bids": {
            "details": [
                {
                    "id": "TEN-0001",
                    "subcontracting": {
                        "subcontracts": [
                            {"id": "1", "subcontractor": {"id": "ORG-0012"}}
                        ]
                    },
                }
            ]
        },
    }
    merge_subcontractor(release_json, subcontractor_data)
    assert release_json == {
        "parties": [
            {"id": "ORG-0001", "roles": ["buyer"]},
            {"id": "ORG-0012", "roles": ["subcontractor"]},
        ],
        "bids": {
            "details": [
                {"id": "TEN-0002", "subcontracting": {"subcontracts": []}},
                {
                    "id": "TEN-0001",
                    "subcontracting": {
                        "subcontracts": [
                            {"id": "1", "subcontractor": {"id": "ORG-0012"}}
                        ]
                    },
                },
            ]
        },
    }
