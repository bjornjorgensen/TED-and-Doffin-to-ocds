# converters/bt_99_Lot.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_review_deadline_description(xml_content: str | bytes) -> dict | None:
    """Parse review deadline description from XML for each lot.

    Extract information about the time limits for review procedures
    as defined in BT-99.

    Args:
        xml_content: The XML content to parse, either as a string or bytes.

    Returns:
        A dictionary containing the parsed data in OCDS format with the following structure:
        {
            "tender": {
                "lots": [
                    {
                        "id": str,
                        "reviewDetails": str
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
        description = lot.xpath(
            "cac:TenderingTerms/cac:AppealTerms/cac:PresentationPeriod/cbc:Description/text()",
            namespaces=namespaces,
        )

        if description:
            lot_data = {"id": lot_id, "reviewDetails": description[0]}
            result["tender"]["lots"].append(lot_data)

    return result if result["tender"]["lots"] else None


def merge_review_deadline_description(
    release_json: dict, review_deadline_description_data: dict | None
) -> None:
    """Merge review deadline description data into the OCDS release.

    Updates the release JSON in-place by adding or updating review details
    for each lot specified in the input data.

    Args:
        release_json: The main OCDS release JSON to be updated. Must contain
            a 'tender' object with a 'lots' array.
        review_deadline_description_data: The parsed review deadline data
            in the same format as returned by parse_review_deadline_description().
            If None, no changes will be made.

    Returns:
        None: The function modifies release_json in-place.

    """
    if not review_deadline_description_data:
        logger.warning("No review deadline description data to merge")
        return

    tender = release_json.setdefault("tender", {})
    existing_lots = tender.setdefault("lots", [])

    for new_lot in review_deadline_description_data["tender"]["lots"]:
        existing_lot = next(
            (lot for lot in existing_lots if lot["id"] == new_lot["id"]),
            None,
        )
        if existing_lot:
            existing_lot["reviewDetails"] = new_lot["reviewDetails"]
        else:
            existing_lots.append(new_lot)

    logger.info(
        "Merged review deadline description data for %d lots",
        len(review_deadline_description_data["tender"]["lots"]),
    )
