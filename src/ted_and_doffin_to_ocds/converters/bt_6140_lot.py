# converters/bt_6140_Lot.py

import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)

NAMESPACES = {
    "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
    "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
    "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
    "efext": "http://data.europa.eu/p27/eforms-ubl-extensions/1",
    "efbc": "http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1",
}


def parse_lot_eu_funds_details(xml_content: str | bytes) -> dict[str, Any] | None:
    """
    Parse the XML content to extract lot EU funds details.

    This function processes the BT-6140-Lot business term, which represents
    further information about the Union programme or project used to at least
    partially finance the procurement for a specific lot.

    Args:
        xml_content: XML content as string or bytes containing procurement data

    Returns:
        Dictionary containing parsed lot EU funds details or None if no data found
    """
    try:
        if isinstance(xml_content, str):
            xml_content = xml_content.encode("utf-8")
        root = etree.fromstring(xml_content)
    except etree.XMLSyntaxError:
        logger.exception("Failed to parse XML")
        raise

    result = {"planning": {"budget": {"finance": []}}}

    funding_descriptions = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']/cac:TenderingTerms/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:Funding/cbc:Description/text()",
        namespaces=NAMESPACES,
    )

    for index, description in enumerate(funding_descriptions, start=1):
        finance_data = {"id": str(index), "description": description}
        result["planning"]["budget"]["finance"].append(finance_data)

    return result if result["planning"]["budget"]["finance"] else None


def merge_lot_eu_funds_details(
    release_json: dict, eu_funds_details: dict | None
) -> None:
    """
    Merge the parsed lot EU funds details into the main OCDS release JSON.

    This function updates the existing finance entries in the release JSON with the
    EU funds details. If a finance entry doesn't exist, it adds a new one to the release.

    Args:
        release_json (dict): The main OCDS release JSON to be updated.
        eu_funds_details (dict): The parsed lot EU funds details to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not eu_funds_details:
        logger.warning("BT-6140-Lot: No lot EU funds details to merge")
        return

    planning = release_json.setdefault("planning", {})
    budget = planning.setdefault("budget", {})
    existing_finance = budget.setdefault("finance", [])

    for new_finance in eu_funds_details["planning"]["budget"]["finance"]:
        existing_entry = next(
            (entry for entry in existing_finance if entry["id"] == new_finance["id"]),
            None,
        )
        if existing_entry:
            existing_entry["description"] = new_finance["description"]
        else:
            existing_finance.append(new_finance)

    logger.info(
        "BT-6140-Lot: Merged lot EU funds details for %d finance entries",
        len(eu_funds_details["planning"]["budget"]["finance"]),
    )
