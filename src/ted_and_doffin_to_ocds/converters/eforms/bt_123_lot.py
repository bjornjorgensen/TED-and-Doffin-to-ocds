import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_electronic_auction_url(xml_content: str | bytes) -> dict | None:
    """Parse electronic auction URL from XML for each lot.

    Extract information about the internet address of the electronic auction
    as defined in BT-123.

    Args:
        xml_content: The XML content to parse, either as a string or bytes.

    Returns:
        A dictionary containing the parsed data in OCDS format with the following structure:
        {
            "tender": {
                "lots": [
                    {
                        "id": str,
                        "techniques": {
                            "electronicAuction": {
                                "url": str
                            }
                        }
                    }
                ]
            }
        }
        Returns None if no relevant data is found.

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

    result = {"tender": {"lots": []}}

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
            lot_data = {
                "id": lot_id,
                "techniques": {"electronicAuction": {"url": auction_url[0]}},
            }
            result["tender"]["lots"].append(lot_data)

    return result if result["tender"]["lots"] else None


def merge_electronic_auction_url(
    release_json: dict, auction_url_data: dict | None
) -> None:
    """Merge electronic auction URL data into the OCDS release.

    Updates the release JSON in-place by adding or updating electronic auction
    information for each lot specified in the input data.

    Args:
        release_json: The main OCDS release JSON to be updated. Must contain
            a 'tender' object with a 'lots' array.
        auction_url_data: The parsed auction URL data
            in the same format as returned by parse_electronic_auction_url().
            If None, no changes will be made.

    Returns:
        None: The function modifies release_json in-place.

    """
    if not auction_url_data:
        logger.info("No electronic auction URL data to merge")
        return

    tender = release_json.setdefault("tender", {})
    existing_lots = tender.setdefault("lots", [])

    for new_lot in auction_url_data["tender"]["lots"]:
        existing_lot = next(
            (lot for lot in existing_lots if lot["id"] == new_lot["id"]),
            None,
        )
        if existing_lot:
            techniques = existing_lot.setdefault("techniques", {})
            electronic_auction = techniques.setdefault("electronicAuction", {})
            electronic_auction["url"] = new_lot["techniques"]["electronicAuction"][
                "url"
            ]
        else:
            existing_lots.append(new_lot)

    logger.info(
        "Merged electronic auction URL data for %d lots",
        len(auction_url_data["tender"]["lots"]),
    )
