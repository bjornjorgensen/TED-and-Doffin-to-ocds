# converters/bt_767_Lot.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_electronic_auction(xml_content: str | bytes) -> dict | None:
    """Parse electronic auction information from XML content.

    Args:
        xml_content (str | bytes): The XML content to parse, either as a string or bytes

    Returns:
        dict | None: A dictionary containing electronic auction information in the format:
            {
                "tender": {
                    "lots": [
                        {
                            "id": str,
                            "techniques": {
                                "hasElectronicAuction": bool
                            }
                        }
                    ]
                }
            }
            Returns None if no valid lots are found.

    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")

    root: etree._Element = etree.fromstring(xml_content)
    namespaces = {
        "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
        "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
        "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
        "efext": "http://data.europa.eu/p27/eforms-ubl-extensions/1",
        "efbc": "http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1",
    }

    result: dict[str, dict] = {"tender": {"lots": []}}

    lots: list = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']",
        namespaces=namespaces,
    )

    for lot in lots:
        lot_id: str = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        auction_indicator: list = lot.xpath(
            "cac:TenderingProcess/cac:AuctionTerms/cbc:AuctionConstraintIndicator/text()",
            namespaces=namespaces,
        )

        if auction_indicator:
            result["tender"]["lots"].append(
                {
                    "id": lot_id,
                    "techniques": {
                        "hasElectronicAuction": auction_indicator[0].lower() == "true",
                    },
                },
            )

    return result if result["tender"]["lots"] else None


def merge_electronic_auction(
    release_json: dict,
    electronic_auction_data: dict | None,
) -> None:
    """Merge electronic auction data into the release JSON.

    Args:
        release_json (dict): The target release JSON to merge data into
        electronic_auction_data (dict | None): Electronic auction data to merge, in the format:
            {
                "tender": {
                    "lots": [
                        {
                            "id": str,
                            "techniques": {
                                "hasElectronicAuction": bool
                            }
                        }
                    ]
                }
            }

    Returns:
        None: Modifies release_json in place

    """
    if not electronic_auction_data:
        logger.warning("No electronic auction data to merge")
        return

    tender: dict = release_json.setdefault("tender", {})
    existing_lots: list = tender.setdefault("lots", [])

    for new_lot in electronic_auction_data["tender"]["lots"]:
        existing_lot: dict | None = next(
            (lot for lot in existing_lots if lot["id"] == new_lot["id"]),
            None,
        )
        if existing_lot:
            existing_lot.setdefault("techniques", {}).update(new_lot["techniques"])
        else:
            existing_lots.append(new_lot)

    logger.info(
        "Merged electronic auction data for %d lots",
        len(electronic_auction_data["tender"]["lots"]),
    )
