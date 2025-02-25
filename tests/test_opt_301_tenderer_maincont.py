# tests/test_opt_301_tenderer_maincont.py

from src.ted_and_doffin_to_ocds.converters.eforms.opt_301_tenderer_maincont import (
    merge_main_contractor,
    parse_main_contractor,
)


def test_parse_main_contractor() -> None:
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
                    <efac:MainContractor>
                        <cbc:ID schemeName="organization">ORG-0005</cbc:ID>
                    </efac:MainContractor>
                </efac:SubContractor>
            </efac:TenderingParty>
        </efac:NoticeResult>
        <efac:Organizations>
            <efac:Organization>
                <efac:Company>
                    <cac:PartyIdentification>
                        <cbc:ID schemeName="organization">ORG-0005</cbc:ID>
                    </cac:PartyIdentification>
                </efac:Company>
            </efac:Organization>
        </efac:Organizations>
    </root>
    """
    result = parse_main_contractor(xml_content)
    assert result == {
        "parties": [{"id": "ORG-0005", "roles": ["tenderer"]}],
        "bids": {
            "details": [
                {
                    "id": "TEN-0001",
                    "subcontracting": {
                        "subcontracts": [
                            {
                                "id": "1",
                                "subcontractor": {"id": "ORG-0012"},
                                "mainContractors": [{"id": "ORG-0005"}],
                            }
                        ]
                    },
                }
            ]
        },
    }


def test_merge_main_contractor() -> None:
    release_json = {
        "parties": [{"id": "ORG-0005", "roles": ["buyer"]}],
        "bids": {
            "details": [{"id": "TEN-0001", "subcontracting": {"subcontracts": []}}]
        },
    }
    main_contractor_data = {
        "parties": [{"id": "ORG-0005", "roles": ["tenderer"]}],
        "bids": {
            "details": [
                {
                    "id": "TEN-0001",
                    "subcontracting": {
                        "subcontracts": [
                            {
                                "id": "1",
                                "subcontractor": {"id": "ORG-0012"},
                                "mainContractors": [{"id": "ORG-0005"}],
                            }
                        ]
                    },
                }
            ]
        },
    }
    merge_main_contractor(release_json, main_contractor_data)
    assert release_json == {
        "parties": [{"id": "ORG-0005", "roles": ["buyer", "tenderer"]}],
        "bids": {
            "details": [
                {
                    "id": "TEN-0001",
                    "subcontracting": {
                        "subcontracts": [
                            {
                                "id": "1",
                                "subcontractor": {"id": "ORG-0012"},
                                "mainContractors": [{"id": "ORG-0005"}],
                            }
                        ]
                    },
                }
            ]
        },
    }


def test_merge_main_contractor_new_data() -> None:
    release_json = {
        "parties": [{"id": "ORG-0001", "roles": ["buyer"]}],
        "bids": {
            "details": [{"id": "TEN-0002", "subcontracting": {"subcontracts": []}}]
        },
    }
    main_contractor_data = {
        "parties": [{"id": "ORG-0005", "roles": ["tenderer"]}],
        "bids": {
            "details": [
                {
                    "id": "TEN-0001",
                    "subcontracting": {
                        "subcontracts": [
                            {
                                "id": "1",
                                "subcontractor": {"id": "ORG-0012"},
                                "mainContractors": [{"id": "ORG-0005"}],
                            }
                        ]
                    },
                }
            ]
        },
    }
    merge_main_contractor(release_json, main_contractor_data)
    assert release_json == {
        "parties": [
            {"id": "ORG-0001", "roles": ["buyer"]},
            {"id": "ORG-0005", "roles": ["tenderer"]},
        ],
        "bids": {
            "details": [
                {"id": "TEN-0002", "subcontracting": {"subcontracts": []}},
                {
                    "id": "TEN-0001",
                    "subcontracting": {
                        "subcontracts": [
                            {
                                "id": "1",
                                "subcontractor": {"id": "ORG-0012"},
                                "mainContractors": [{"id": "ORG-0005"}],
                            }
                        ]
                    },
                },
            ]
        },
    }
