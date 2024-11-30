# converters/bt_720_Tender.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_tender_value(xml_content: str) -> dict | None:
    """
    Parse the XML content to extract the tender value information.

    Args:
        xml_content (str): The XML content to parse.

    Returns:
        Optional[Dict]: A dictionary containing the parsed data if found, None otherwise.
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

    result = {"bids": {"details": []}, "awards": []}

    lot_tenders = root.xpath("//efac:LotTender", namespaces=namespaces)

    for lot_tender in lot_tenders:
        tender_id = lot_tender.xpath(
            "cbc:ID[@schemeName='tender']/text()",
            namespaces=namespaces,
        )
        payable_amount = lot_tender.xpath(
            "cac:LegalMonetaryTotal/cbc:PayableAmount/text()",
            namespaces=namespaces,
        )
        currency = lot_tender.xpath(
            "cac:LegalMonetaryTotal/cbc:PayableAmount/@currencyID",
            namespaces=namespaces,
        )
        lot_id = lot_tender.xpath(
            "efac:TenderLot/cbc:ID[@schemeName='Lot']/text()",
            namespaces=namespaces,
        )

        if tender_id and payable_amount and currency and lot_id:
            bid = {
                "id": tender_id[0],
                "value": {"amount": float(payable_amount[0]), "currency": currency[0]},
            }
            result["bids"]["details"].append(bid)

            # Find corresponding LotResult
            lot_result = root.xpath(
                f"//efac:LotResult[efac:LotTender/cbc:ID[@schemeName='tender']/text()='{tender_id[0]}']",
                namespaces=namespaces,
            )
            if lot_result:
                result_id = lot_result[0].xpath(
                    "cbc:ID[@schemeName='result']/text()",
                    namespaces=namespaces,
                )
                if result_id:
                    award = {
                        "id": result_id[0],
                        "value": {
                            "amount": float(payable_amount[0]),
                            "currency": currency[0],
                        },
                        "relatedLots": [lot_id[0]],
                    }
                    result["awards"].append(award)

    return result if result["bids"]["details"] or result["awards"] else None


def merge_tender_value(release_json: dict, tender_value_data: dict | None) -> None:
    """
    Merge the parsed tender value data into the main OCDS release JSON.

    Args:
        release_json (Dict): The main OCDS release JSON to be updated.
        tender_value_data (Optional[Dict]): The parsed tender value data to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not tender_value_data:
        logger.warning("No tender value data to merge")
        return

    # Merge bids
    if "bids" not in release_json:
        release_json["bids"] = {"details": []}

    for bid in tender_value_data["bids"]["details"]:
        existing_bid = next(
            (b for b in release_json["bids"]["details"] if b["id"] == bid["id"]),
            None,
        )
        if existing_bid:
            existing_bid.update(bid)
        else:
            release_json["bids"]["details"].append(bid)

    # Merge awards
    if "awards" not in release_json:
        release_json["awards"] = []

    for award in tender_value_data["awards"]:
        existing_award = next(
            (a for a in release_json["awards"] if a["id"] == award["id"]),
            None,
        )
        if existing_award:
            existing_award.update(award)
        else:
            release_json["awards"].append(award)

    logger.info(
        "Merged tender value data for %d bids and %d awards",
        len(tender_value_data["bids"]["details"]),
        len(tender_value_data["awards"]),
    )
