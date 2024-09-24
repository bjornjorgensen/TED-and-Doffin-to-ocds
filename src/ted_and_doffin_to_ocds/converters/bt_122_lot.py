# converters/bt_122_Lot.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)


def parse_electronic_auction_description(xml_content):
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
        auction_description = lot.xpath(
            "cac:TenderingProcess/cac:AuctionTerms/cbc:Description/text()",
            namespaces=namespaces,
        )

        if auction_description:
            result["lots"].append(
                {
                    "id": lot_id,
                    "techniques": {
                        "electronicAuction": {"description": auction_description[0]},
                    },
                },
            )

    return result if result["lots"] else None


def merge_electronic_auction_description(release_json, auction_description_data):
    if not auction_description_data:
        logger.warning("No Electronic Auction Description data to merge")
        return

    tender = release_json.setdefault("tender", {})
    existing_lots = tender.setdefault("lots", [])

    for new_lot in auction_description_data["lots"]:
        existing_lot = next(
            (lot for lot in existing_lots if lot["id"] == new_lot["id"]),
            None,
        )
        if existing_lot:
            existing_lot.setdefault("techniques", {}).setdefault(
                "electronicAuction",
                {},
            )["description"] = new_lot["techniques"]["electronicAuction"]["description"]
        else:
            existing_lots.append(new_lot)

    logger.info(
        "Merged Electronic Auction Description data for %d lots",
        len(auction_description_data["lots"]),
    )
