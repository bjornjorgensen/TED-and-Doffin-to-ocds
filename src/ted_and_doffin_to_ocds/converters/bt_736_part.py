# converters/bt_736_part.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)


def parse_reserved_execution_part(xml_content):
    """
    Parse the XML content to extract the reserved execution information for the part.

    Args:
        xml_content (str or bytes): The XML content to parse.

    Returns:
        dict: A dictionary containing the parsed reserved execution data for the part.
        None: If no relevant data is found or if the value is not "yes".
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

    xpath_query = "/*/cac:ProcurementProjectLot[cbc:ID/@schemeName='part']/cac:TenderingTerms/cac:ContractExecutionRequirement[cbc:ExecutionRequirementCode/@listName='reserved-execution']/cbc:ExecutionRequirementCode"
    reserved_execution = root.xpath(xpath_query, namespaces=namespaces)

    if reserved_execution and reserved_execution[0].text.lower() == "yes":
        return {"tender": {"contractTerms": {"reservedExecution": True}}}

    return None


def merge_reserved_execution_part(release_json, reserved_execution_data):
    """
    Merge the parsed reserved execution data for the part into the main OCDS release JSON.

    Args:
        release_json (dict): The main OCDS release JSON to be updated.
        reserved_execution_data (dict): The parsed reserved execution data for the part to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not reserved_execution_data:
        logger.warning("No reserved execution data for part to merge")
        return

    tender = release_json.setdefault("tender", {})
    contract_terms = tender.setdefault("contractTerms", {})
    contract_terms["reservedExecution"] = reserved_execution_data["tender"][
        "contractTerms"
    ]["reservedExecution"]

    logger.info("Merged reserved execution data for part")
