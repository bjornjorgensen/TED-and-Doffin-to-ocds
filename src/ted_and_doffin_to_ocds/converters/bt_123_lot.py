# converters/bt_123_Lot.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_electronic_auction_url(xml_content):
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

    result = {"lots": []}

    lots = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']",
        namespaces=namespaces,
    )

    for lot in lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        auction_url = lot.xpath(
            "cac:TenderingProcess/cac:AuctionTerms/cbc:AuctionURI/text()",
            namespaces=namespaces,
        )

        if auction_url:
            result["lots"].append(
                {
                    "id": lot_id,
                    "techniques": {"electronicAuction": {"url": auction_url[0]}},
                },
            )

    return result if result["lots"] else None


def merge_electronic_auction_url(release_json, auction_url_data) -> None:
    if not auction_url_data:
        logger.warning("No Electronic Auction URL data to merge")
        return

    tender = release_json.setdefault("tender", {})
    existing_lots = tender.setdefault("lots", [])

    for new_lot in auction_url_data["lots"]:
        existing_lot = next(
            (lot for lot in existing_lots if lot["id"] == new_lot["id"]),
            None,
        )
        if existing_lot:
            existing_lot.setdefault("techniques", {}).setdefault(
                "electronicAuction",
                {},
            )["url"] = new_lot["techniques"]["electronicAuction"]["url"]
        else:
            existing_lots.append(new_lot)

    logger.info(
        "Merged Electronic Auction URL data for %d lots",
        len(auction_url_data["lots"]),
    )
