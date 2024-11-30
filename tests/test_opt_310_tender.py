# tests/test_opt_310_tender.py

from ted_and_doffin_to_ocds.converters.opt_310_tender import (
    merge_tendering_party_id_reference,
    parse_tendering_party_id_reference,
)


def test_parse_tendering_party_id_reference() -> None:
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
          xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1">
        <efac:NoticeResult>
            <efac:LotTender>
                <cbc:ID schemeName="tender">TEN-0001</cbc:ID>
                <efac:TenderingParty>
                    <cbc:ID schemeName="tendering-party">TPA-0001</cbc:ID>
                </efac:TenderingParty>
                <efac:TenderLot>
                    <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
                </efac:TenderLot>
            </efac:LotTender>
            <efac:TenderingParty>
                <cbc:ID schemeName="tendering-party">TPA-0001</cbc:ID>
                <efac:Tenderer>
                    <cbc:ID schemeName="organization">ORG-0011</cbc:ID>
                </efac:Tenderer>
            </efac:TenderingParty>
        </efac:NoticeResult>
    </root>
    """
    result = parse_tendering_party_id_reference(xml_content)
    assert result == {
        "parties": [{"id": "ORG-0011", "roles": ["tenderer"]}],
        "bids": {"details": [{"id": "TEN-0001", "tenderers": [{"id": "ORG-0011"}]}]},
    }


def test_merge_tendering_party_id_reference() -> None:
    release_json = {
        "parties": [{"id": "ORG-0011", "roles": ["buyer"]}],
        "bids": {"details": [{"id": "TEN-0001", "tenderers": []}]},
    }
    tendering_party_data = {
        "parties": [{"id": "ORG-0011", "roles": ["tenderer"]}],
        "bids": {"details": [{"id": "TEN-0001", "tenderers": [{"id": "ORG-0011"}]}]},
    }
    merge_tendering_party_id_reference(release_json, tendering_party_data)
    assert release_json == {
        "parties": [{"id": "ORG-0011", "roles": ["buyer", "tenderer"]}],
        "bids": {"details": [{"id": "TEN-0001", "tenderers": [{"id": "ORG-0011"}]}]},
    }


def test_merge_tendering_party_id_reference_new_data() -> None:
    release_json = {
        "parties": [{"id": "ORG-0001", "roles": ["buyer"]}],
        "bids": {"details": [{"id": "TEN-0002", "tenderers": []}]},
    }
    tendering_party_data = {
        "parties": [{"id": "ORG-0011", "roles": ["tenderer"]}],
        "bids": {"details": [{"id": "TEN-0001", "tenderers": [{"id": "ORG-0011"}]}]},
    }
    merge_tendering_party_id_reference(release_json, tendering_party_data)
    assert release_json == {
        "parties": [
            {"id": "ORG-0001", "roles": ["buyer"]},
            {"id": "ORG-0011", "roles": ["tenderer"]},
        ],
        "bids": {
            "details": [
                {"id": "TEN-0002", "tenderers": []},
                {"id": "TEN-0001", "tenderers": [{"id": "ORG-0011"}]},
            ]
        },
    }
