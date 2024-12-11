"""Converter for BT-736-Part: Reserved execution for sheltered employment programmes.

This module handles the extraction and mapping of contract reserved execution information
from eForms notices to OCDS format for Parts, specifically whether contracts must be
performed under sheltered employment programmes.
"""

import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_reserved_execution_part(
    xml_content: str | bytes,
) -> dict[str, dict[str, bool]] | None:
    """Parse whether a part is reserved for sheltered employment programmes.

    Checks if the contract execution must be performed under sheltered employment
    programmes by examining the ExecutionRequirementCode with listName='reserved-execution'.
    If the code is 'yes', sets tender.contractTerms.reservedExecution to true.

    Args:
        xml_content: XML content to parse

    Returns:
        dict: Dictionary in format:
            {
                "tender": {
                    "contractTerms": {
                        "reservedExecution": bool
                    }
                }
            }
        None: If no relevant data found or value is not "yes"

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

    xpath_query = "/*/cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']/cac:TenderingTerms/cac:ContractExecutionRequirement[cbc:ExecutionRequirementCode/@listName='reserved-execution']/cbc:ExecutionRequirementCode"
    reserved_execution = root.xpath(xpath_query, namespaces=namespaces)

    if reserved_execution and reserved_execution[0].text.lower() == "yes":
        return {"tender": {"contractTerms": {"reservedExecution": True}}}

    return None


def merge_reserved_execution_part(
    release_json: dict, reserved_execution_data: dict[str, dict[str, bool]] | None
) -> None:
    """Merge reserved execution data for the part into the OCDS release.

    Updates or adds tender.contractTerms.reservedExecution in the release JSON
    to indicate whether contract execution must be performed under sheltered
    employment programmes.

    Args:
        release_json: Target release JSON to update
        reserved_execution_data: Reserved execution data to merge in format:
            {
                "tender": {
                    "contractTerms": {
                        "reservedExecution": bool
                    }
                }
            }

    Note:
        Updates release_json in-place

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
