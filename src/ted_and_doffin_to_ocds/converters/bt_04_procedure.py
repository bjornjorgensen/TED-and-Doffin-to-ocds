from typing import Any
import logging
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


def parse_procedure_identifier(xml_content: str | bytes) -> dict[str, Any] | None:
    """
    Parse the procedure identifier from XML content.

    Args:
        xml_content: XML string or bytes to parse

    Returns:
        Dictionary containing tender ID or None if not found

    Raises:
        etree.XMLSyntaxError: If XML content is invalid
    """
    try:
        if isinstance(xml_content, str):
            xml_content = xml_content.encode("utf-8")

        root = etree.fromstring(xml_content)
        contract_folder_id_elements = root.xpath(
            "//cbc:ContractFolderID",
            namespaces=NAMESPACES,
        )

        if contract_folder_id_elements:
            contract_folder_id = contract_folder_id_elements[0].text
            if contract_folder_id and contract_folder_id.strip():
                logger.info("Found procedure identifier: %s", contract_folder_id)
                return {"tender": {"id": contract_folder_id.strip()}}
            logger.warning("No valid procedure identifier found in XML")
        else:
            logger.warning("No valid procedure identifier found in XML")
            return None

    except etree.XMLSyntaxError:
        logger.exception("Failed to parse XML content")
        raise


def merge_procedure_identifier(
    release_json: dict[str, Any], procedure_identifier_data: dict[str, Any] | None
) -> None:
    """
    Merge procedure identifier data into the release JSON.

    Args:
        release_json: The target release JSON to update
        procedure_identifier_data: The procedure identifier data to merge
    """
    if not procedure_identifier_data:
        logger.debug("No procedure identifier data to merge")
        return

    tender = release_json.setdefault("tender", {})
    tender.update(procedure_identifier_data["tender"])
    logger.info(
        "Merged procedure identifier: %s", procedure_identifier_data["tender"]["id"]
    )
