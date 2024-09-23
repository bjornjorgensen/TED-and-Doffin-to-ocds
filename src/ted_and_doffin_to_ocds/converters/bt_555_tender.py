# converters/bt_555_Tender.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)


def parse_subcontracting_percentage(xml_content):
    """
    Parse the XML content to extract subcontracting percentage information for each tender.

    This function processes the BT-555-Tender business term, which represents the estimated
    percentage of the contract that the contractor will subcontract to third parties.

    Args:
        xml_content (str): The XML content to parse.

    Returns:
        dict: A dictionary containing the parsed subcontracting percentage data in the format:
              {
                  "bids": {
                      "details": [
                          {
                              "id": "tender_id",
                              "subcontracting": {
                                  "minimumPercentage": float,
                                  "maximumPercentage": float
                              },
                              "relatedLots": ["lot_id"]
                          },
                          ...
                      ]
                  }
              }
        None: If no relevant data is found.

    Raises:
        etree.XMLSyntaxError: If the input is not valid XML.
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
        "//efac:noticeResult/efac:LotTender",
        namespaces=namespaces,
    )

    for lot_tender in lot_tenders:
        tender_id = lot_tender.xpath(
            "cbc:ID[@schemeName='tender']/text()",
            namespaces=namespaces,
        )
        subcontracting_percentage = lot_tender.xpath(
            "efac:SubcontractingTerm[efbc:TermCode/@listName='applicability']/efbc:TermPercent/text()",
            namespaces=namespaces,
        )
        related_lots = lot_tender.xpath(
            "efac:TenderLot/cbc:ID[@schemeName='Lot']/text()",
            namespaces=namespaces,
        )

        if tender_id and subcontracting_percentage:
            percentage = float(subcontracting_percentage[0]) / 100
            bid_data = {
                "id": tender_id[0],
                "subcontracting": {
                    "minimumPercentage": percentage,
                    "maximumPercentage": percentage,
                },
                "relatedLots": list(
                    set(related_lots),
                ),  # Use a set to ensure unique lot IDs
            }
            result["bids"]["details"].append(bid_data)

    return result if result["bids"]["details"] else None


def merge_subcontracting_percentage(release_json, subcontracting_data):
    """
    Merge the parsed subcontracting percentage data into the main OCDS release JSON.

    This function updates the existing bids in the release JSON with the subcontracting
    percentage information. If a bid doesn't exist, it adds a new bid to the release.

    Args:
        release_json (dict): The main OCDS release JSON to be updated.
        subcontracting_data (dict): The parsed subcontracting percentage data to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not subcontracting_data:
        logger.warning("BT-555-Tender: No subcontracting percentage data to merge")
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
        f"BT-555-Tender: Merged subcontracting percentage data for {len(subcontracting_data['bids']['details'])} bids",
    )
