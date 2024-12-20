# tests/test_bt_13714_Tender.py
from lxml import etree

from ted_and_doffin_to_ocds.converters.bt_13714_tender import (
    merge_tender_lot_identifier,
    parse_tender_lot_identifier,
)


def create_xml_with_lot_tenders(lot_tenders):
    root = etree.Element(
        "root",
        nsmap={
            "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
            "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
            "efext": "http://data.europa.eu/p27/eforms-ubl-extensions/1",
            "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
        },
    )
    for tender_id, lot_id in lot_tenders:
        lot_tender = etree.SubElement(
            root,
            "{http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1}LotTender",
        )
        tender_id_elem = etree.SubElement(
            lot_tender,
            "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}ID",
        )
        tender_id_elem.text = tender_id
        tender_id_elem.set("schemeName", "tender")
        tender_lot = etree.SubElement(
            lot_tender,
            "{http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1}TenderLot",
        )
        lot_id_elem = etree.SubElement(
            tender_lot,
            "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}ID",
        )
        lot_id_elem.text = lot_id
        lot_id_elem.set("schemeName", "Lot")
    return etree.tostring(root)


def test_parse_tender_lot_identifier_single() -> None:
    xml_content = create_xml_with_lot_tenders([("TEN-0001", "LOT-0001")])
    result = parse_tender_lot_identifier(xml_content)
    assert result == {
        "bids": {"details": [{"id": "TEN-0001", "relatedLots": ["LOT-0001"]}]},
    }


def test_parse_tender_lot_identifier_multiple() -> None:
    xml_content = create_xml_with_lot_tenders(
        [("TEN-0001", "LOT-0001"), ("TEN-0002", "LOT-0002"), ("TEN-0003", "LOT-0003")],
    )
    result = parse_tender_lot_identifier(xml_content)
    assert result == {
        "bids": {
            "details": [
                {"id": "TEN-0001", "relatedLots": ["LOT-0001"]},
                {"id": "TEN-0002", "relatedLots": ["LOT-0002"]},
                {"id": "TEN-0003", "relatedLots": ["LOT-0003"]},
            ],
        },
    }


def test_parse_tender_lot_identifier_empty() -> None:
    xml_content = create_xml_with_lot_tenders([])
    result = parse_tender_lot_identifier(xml_content)
    assert result is None


def test_merge_tender_lot_identifier_new_bids() -> None:
    release_json = {}
    tender_lot_identifier_data = {
        "bids": {
            "details": [
                {"id": "TEN-0001", "relatedLots": ["LOT-0001"]},
                {"id": "TEN-0002", "relatedLots": ["LOT-0002"]},
            ],
        },
    }
    merge_tender_lot_identifier(release_json, tender_lot_identifier_data)
    assert release_json == {
        "bids": {
            "details": [
                {"id": "TEN-0001", "relatedLots": ["LOT-0001"]},
                {"id": "TEN-0002", "relatedLots": ["LOT-0002"]},
            ],
        },
    }


def test_merge_tender_lot_identifier_existing_bids() -> None:
    release_json = {
        "bids": {"details": [{"id": "TEN-0001", "relatedLots": ["LOT-0001"]}]},
    }
    tender_lot_identifier_data = {
        "bids": {
            "details": [
                {"id": "TEN-0001", "relatedLots": ["LOT-0002"]},
                {"id": "TEN-0002", "relatedLots": ["LOT-0003"]},
            ],
        },
    }
    merge_tender_lot_identifier(release_json, tender_lot_identifier_data)
    assert release_json == {
        "bids": {
            "details": [
                {"id": "TEN-0001", "relatedLots": ["LOT-0001", "LOT-0002"]},
                {"id": "TEN-0002", "relatedLots": ["LOT-0003"]},
            ],
        },
    }


def test_merge_tender_lot_identifier_empty_data() -> None:
    release_json = {"bids": {"details": []}}
    merge_tender_lot_identifier(release_json, None)
    assert release_json == {"bids": {"details": []}}
