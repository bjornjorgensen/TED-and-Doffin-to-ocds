# converters/bt_553_Tender.py

import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)


def parse_subcontracting_value(
    xml_content: str | bytes,
) -> dict[str, Any] | None:
    """Parse the subcontracting value (BT-553) for procurement project tenders from XML content.

    Args:
        xml_content: XML string or bytes containing the procurement data

    Returns:
        Dict containing the parsed subcontracting value data in OCDS format, or None if no data found.
        Format:
        {
            "bids": {
                "details": [
                    {
                        "id": "TEN-0001",
                        "subcontracting": {
                            "value": {
                                "amount": 9999999.99,
                                "currency": "EUR"
                            }
                        },
                        "relatedLots": [
                            "LOT-0001"
                        ]
                    }
                ]
            }
        }

    """
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
        "//efac:NoticeResult/efac:LotTender",
        namespaces=namespaces,
    )

    for lot_tender in lot_tenders:
        tender_id = lot_tender.xpath(
            "cbc:ID[@schemeName='tender']/text()",
            namespaces=namespaces,
        )
        subcontracting_amount = lot_tender.xpath(
            "efac:SubcontractingTerm[efbc:TermCode/@listName='applicability']/efbc:TermAmount/text()",
            namespaces=namespaces,
        )
        currency = lot_tender.xpath(
            "efac:SubcontractingTerm[efbc:TermCode/@listName='applicability']/efbc:TermAmount/@currencyID",
            namespaces=namespaces,
        )
        related_lot = lot_tender.xpath(
            "efac:TenderLot/cbc:ID[@schemeName='Lot']/text()",
            namespaces=namespaces,
        )

        if tender_id and subcontracting_amount and currency:
            bid_data = {
                "id": tender_id[0],
                "subcontracting": {
                    "value": {
                        "amount": float(subcontracting_amount[0]),
                        "currency": currency[0],
                    },
                },
                "relatedLots": related_lot,
            }
            result["bids"]["details"].append(bid_data)

    return result if result["bids"]["details"] else None


def merge_subcontracting_value(
    release_json: dict[str, Any],
    subcontracting_data: dict[str, Any] | None,
) -> None:
    """Merge subcontracting value data into the release JSON.

    Args:
        release_json: The main release JSON to merge data into
        subcontracting_data: The subcontracting value data to merge from

    Returns:
        None - modifies release_json in place

    """
    if not subcontracting_data:
        logger.warning("No subcontracting value data to merge")
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
            # Replace the relatedLots instead of extending
            existing_bid["relatedLots"] = new_bid.get("relatedLots", [])
        else:
            existing_bids.append(new_bid)

    logger.info(
        "Merged subcontracting value data for %d bids",
        len(subcontracting_data["bids"]["details"]),
    )
