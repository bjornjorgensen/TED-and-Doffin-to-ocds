# converters/bt_554_Tender.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)


def parse_subcontracting_description(xml_content):
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")
    root = etree.fromstring(xml_content)
    namespaces = {
        "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
        "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
        "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
        "efext": "http://data.europa.eu/p27/eforms-ubl-extensions/1",
        "efbc": "http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1",
    }

    result = {"bids": {"details": []}}

    lot_tenders = root.xpath(
        "//efac:noticeResult/efac:LotTender",
        namespaces=namespaces,
    )

    for lot_tender in lot_tenders:
        tender_id = lot_tender.xpath(
            "cbc:ID[@schemeName='tender']/text()",
            namespaces=namespaces,
        )
        subcontracting_description = lot_tender.xpath(
            "efac:SubcontractingTerm[efbc:TermCode/@listName='applicability']/efbc:TermDescription/text()",
            namespaces=namespaces,
        )
        related_lots = lot_tender.xpath(
            "efac:TenderLot/cbc:ID[@schemeName='Lot']/text()",
            namespaces=namespaces,
        )

        if tender_id and subcontracting_description:
            bid_data = {
                "id": tender_id[0],
                "subcontracting": {"description": subcontracting_description[0]},
                "relatedLots": list(
                    set(related_lots),
                ),  # Use a set to ensure unique lot IDs
            }
            result["bids"]["details"].append(bid_data)

    return result if result["bids"]["details"] else None


def merge_subcontracting_description(release_json, subcontracting_data):
    if not subcontracting_data:
        logger.warning("No subcontracting description data to merge")
        return

    existing_bids = release_json.setdefault("bids", {}).setdefault("details", [])

    for new_bid in subcontracting_data["bids"]["details"]:
        existing_bid = next(
            (bid for bid in existing_bids if bid["id"] == new_bid["id"]),
            None,
        )
        if existing_bid:
            existing_bid.setdefault("subcontracting", {}).update(
                new_bid["subcontracting"],
            )
            existing_bid["relatedLots"] = list(
                set(
                    existing_bid.get("relatedLots", [])
                    + new_bid.get("relatedLots", []),
                ),
            )
        else:
            existing_bids.append(new_bid)

    logger.info(
        "Merged subcontracting description data for %d bids",
        len(subcontracting_data["bids"]["details"]),
    )
