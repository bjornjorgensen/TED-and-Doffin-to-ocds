# converters/bt_75_Lot.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)


def parse_guarantee_required_description(xml_content):
    """
    Parse the XML content to extract the guarantee required description for each lot.

    Args:
        xml_content (str or bytes): The XML content to parse.

    Returns:
        dict: A dictionary containing the parsed guarantee required description data.
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

    xpath_query = "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']"
    lots = root.xpath(xpath_query, namespaces=namespaces)

    for lot in lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        guarantee_description = lot.xpath(
            "cac:TenderingTerms/cac:RequiredFinancialGuarantee/cbc:Description/text()",
            namespaces=namespaces,
        )

        if guarantee_description:
            lot_data = {
                "id": lot_id,
                "submissionTerms": {"depositsGuarantees": guarantee_description[0]},
            }
            result["tender"]["lots"].append(lot_data)

    return result if result["tender"]["lots"] else None


def merge_guarantee_required_description(release_json, guarantee_description_data):
    """
    Merge the parsed guarantee required description data into the main OCDS release JSON.

    Args:
        release_json (dict): The main OCDS release JSON to be updated.
        guarantee_description_data (dict): The parsed guarantee required description data to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not guarantee_description_data:
        logger.warning("No guarantee required description data to merge")
        return

    tender = release_json.setdefault("tender", {})
    existing_lots = tender.setdefault("lots", [])

    for new_lot in guarantee_description_data["tender"]["lots"]:
        existing_lot = next(
            (lot for lot in existing_lots if lot["id"] == new_lot["id"]),
            None,
        )
        if existing_lot:
            existing_lot.setdefault("submissionTerms", {}).update(
                new_lot["submissionTerms"],
            )
        else:
            existing_lots.append(new_lot)

    logger.info(
        "Merged guarantee required description data for %d lots",
        len(guarantee_description_data["tender"]["lots"]),
    )
