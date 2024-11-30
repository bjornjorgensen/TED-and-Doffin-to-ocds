# converters/bt_99_Lot.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_review_deadline_description(xml_content):
    """
    Parse the XML content to extract the review deadline description for each lot.

    Args:
        xml_content (str): The XML content to parse.

    Returns:
        dict: A dictionary containing the parsed review deadline description data.
        None: If no relevant data is found.
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
            ".//cac:TenderingTerms/cac:AppealTerms/cac:PresentationPeriod/cbc:Description/text()",
            namespaces=namespaces,
        )

        if description:
            lot_data = {"id": lot_id, "reviewDetails": description[0]}
            result["tender"]["lots"].append(lot_data)

    return result if result["tender"]["lots"] else None


def merge_review_deadline_description(
    release_json, review_deadline_description_data
) -> None:
    """
    Merge the parsed review deadline description data into the main OCDS release JSON.

    Args:
        release_json (dict): The main OCDS release JSON to be updated.
        review_deadline_description_data (dict): The parsed review deadline description data to be merged.

    Returns:
        None: The function updates the release_json in-place.
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
