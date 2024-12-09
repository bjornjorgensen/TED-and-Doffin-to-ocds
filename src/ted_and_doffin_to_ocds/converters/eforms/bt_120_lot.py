import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_no_negotiation_necessary(xml_content: str | bytes) -> dict | None:
    """Parse no negotiation necessary information from XML for each lot.

    Extract information about whether the buyer reserves the right to award the contract
    without negotiation as defined in BT-120.

    Args:
        xml_content: The XML content to parse, either as a string or bytes.

    Returns:
        A dictionary containing the parsed data in OCDS format with the following structure:
        {
            "tender": {
                "lots": [
                    {
                        "id": str,
                        "secondStage": {
                            "noNegotiationNecessary": bool
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
        no_negotiation = lot.xpath(
            "cac:TenderingTerms/cac:AwardingTerms/cbc:NoFurtherNegotiationIndicator/text()",
            namespaces=namespaces,
        )

        if no_negotiation:
            lot_data = {
                "id": lot_id,
                "secondStage": {
                    "noNegotiationNecessary": no_negotiation[0].lower() == "true"
                },
            }
            result["tender"]["lots"].append(lot_data)

    return result if result["tender"]["lots"] else None


def merge_no_negotiation_necessary(
    release_json: dict, no_negotiation_data: dict | None
) -> None:
    """Merge no negotiation necessary data into the OCDS release.

    Updates the release JSON in-place by adding or updating second stage information
    for each lot specified in the input data.

    Args:
        release_json: The main OCDS release JSON to be updated. Must contain
            a 'tender' object with a 'lots' array.
        no_negotiation_data: The parsed no negotiation data
            in the same format as returned by parse_no_negotiation_necessary().
            If None, no changes will be made.

    Returns:
        None: The function modifies release_json in-place.

    """
    if not no_negotiation_data:
        logger.info("No negotiation necessary data to merge")
        return

    tender = release_json.setdefault("tender", {})
    existing_lots = tender.setdefault("lots", [])

    for new_lot in no_negotiation_data["tender"]["lots"]:
        existing_lot = next(
            (lot for lot in existing_lots if lot["id"] == new_lot["id"]),
            None,
        )
        if existing_lot:
            second_stage = existing_lot.setdefault("secondStage", {})
            second_stage["noNegotiationNecessary"] = new_lot["secondStage"][
                "noNegotiationNecessary"
            ]
        else:
            existing_lots.append(new_lot)

    logger.info(
        "Merged no negotiation necessary data for %d lots",
        len(no_negotiation_data["tender"]["lots"]),
    )
