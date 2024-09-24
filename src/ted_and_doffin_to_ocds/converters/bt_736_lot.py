# converters/bt_736_Lot.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)


def parse_reserved_execution(xml_content):
    """
    Parse the XML content to extract the reserved execution information for each lot.

    Args:
        xml_content (str): The XML content to parse.

    Returns:
        dict: A dictionary containing the parsed reserved execution data.
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
        reserved_execution = lot.xpath(
            ".//cac:TenderingTerms/cac:ContractExecutionRequirement[cbc:ExecutionRequirementCode/@listName='reserved-execution']/cbc:ExecutionRequirementCode/text()",
            namespaces=namespaces,
        )

        if reserved_execution and reserved_execution[0].lower() == "yes":
            lot_data = {"id": lot_id, "contractTerms": {"reservedExecution": True}}
            result["tender"]["lots"].append(lot_data)

    return result if result["tender"]["lots"] else None


def merge_reserved_execution(release_json, reserved_execution_data):
    """
    Merge the parsed reserved execution data into the main OCDS release JSON.

    Args:
        release_json (dict): The main OCDS release JSON to be updated.
        reserved_execution_data (dict): The parsed reserved execution data to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not reserved_execution_data:
        logger.warning("No reserved execution data to merge")
        return

    tender = release_json.setdefault("tender", {})
    existing_lots = tender.setdefault("lots", [])

    for new_lot in reserved_execution_data["tender"]["lots"]:
        existing_lot = next(
            (lot for lot in existing_lots if lot["id"] == new_lot["id"]),
            None,
        )
        if existing_lot:
            existing_lot.setdefault("contractTerms", {}).update(
                new_lot["contractTerms"],
            )
        else:
            existing_lots.append(new_lot)

    logger.info(
        "Merged reserved execution data for %d lots",
        len(reserved_execution_data["tender"]["lots"]),
    )
