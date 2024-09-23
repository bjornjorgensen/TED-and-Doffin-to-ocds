# converters/BT_70_Lot.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)


def parse_lot_performance_terms(xml_content):
    """
    Parse the XML content to extract the performance terms for each lot.

    Args:
        xml_content (str): The XML content to parse.

    Returns:
        dict: A dictionary containing the parsed performance terms data.
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

    result = {"lots": []}

    lots = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']",
        namespaces=namespaces,
    )

    for lot in lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        performance_terms = lot.xpath(
            "cac:TenderingTerms/cac:ContractExecutionRequirement[cbc:ExecutionRequirementCode/@listName='conditions']/cbc:Description/text()",
            namespaces=namespaces,
        )

        if performance_terms:
            result["lots"].append(
                {
                    "id": lot_id,
                    "contractTerms": {"performanceTerms": performance_terms[0]},
                },
            )

    return result if result["lots"] else None


def merge_lot_performance_terms(release_json, lot_performance_terms_data):
    """
    Merge the parsed performance terms data into the main OCDS release JSON.

    Args:
        release_json (dict): The main OCDS release JSON to be updated.
        lot_performance_terms_data (dict): The parsed performance terms data to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not lot_performance_terms_data:
        logger.warning("No Lot Performance Terms data to merge")
        return

    tender = release_json.setdefault("tender", {})
    existing_lots = tender.setdefault("lots", [])

    for new_lot in lot_performance_terms_data["lots"]:
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
        f"Merged Lot Performance Terms data for {len(lot_performance_terms_data['lots'])} lots",
    )
