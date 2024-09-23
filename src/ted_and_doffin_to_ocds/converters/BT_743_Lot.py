# converters/BT_743_Lot.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)

einvoicing_mapping = {
    "required": "Required",
    "allowed": "Allowed",
    "notAllowed": "Not allowed",
}


def parse_electronic_invoicing(xml_content):
    """
    Parse the XML content to extract the electronic invoicing policy for each lot.

    Args:
        xml_content (str or bytes): The XML content to parse.

    Returns:
        dict: A dictionary containing the parsed electronic invoicing policy data.
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
        einvoicing_code = lot.xpath(
            ".//cac:ContractExecutionRequirement[cbc:ExecutionRequirementCode/@listName='einvoicing']/cbc:ExecutionRequirementCode/text()",
            namespaces=namespaces,
        )

        if einvoicing_code:
            lot_data = {
                "id": lot_id,
                "contractTerms": {"electronicInvoicingPolicy": einvoicing_code[0]},
            }
            result["tender"]["lots"].append(lot_data)

    return result if result["tender"]["lots"] else None


def merge_electronic_invoicing(release_json, electronic_invoicing_data):
    """
    Merge the parsed electronic invoicing policy data into the main OCDS release JSON.

    Args:
        release_json (dict): The main OCDS release JSON to be updated.
        electronic_invoicing_data (dict): The parsed electronic invoicing policy data to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not electronic_invoicing_data:
        logger.warning("No electronic invoicing policy data to merge")
        return

    tender = release_json.setdefault("tender", {})
    existing_lots = tender.setdefault("lots", [])

    for new_lot in electronic_invoicing_data["tender"]["lots"]:
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
        f"Merged electronic invoicing policy data for {len(electronic_invoicing_data['tender']['lots'])} lots",
    )
