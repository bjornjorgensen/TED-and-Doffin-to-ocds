import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)


def parse_contract_technical_identifier(
    xml_content: str | bytes,
) -> dict[str, Any] | None:
    """
    Parse contract technical identifiers from settled contracts.

    For each settled contract:
    - Gets contract ID
    - Creates basic contract entries
    - Skips contracts that already exist

    Args:
        xml_content: XML content containing contract data

    Returns:
        Optional[Dict]: Dictionary containing contracts with IDs, or None if no data.
        Example structure:
        {
            "contracts": [
                {
                    "id": "contract_id"
                }
            ]
        }
    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")
    root = etree.fromstring(xml_content)
    namespaces = {
        "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
        "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
        "efext": "http://data.europa.eu/p27/eforms-ubl-extensions/1",
        "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
    }

    result = {"contracts": []}

    # Parse SettledContract information
    settled_contracts = root.xpath(
        "//efac:NoticeResult/efac:SettledContract", namespaces=namespaces
    )

    for settled_contract in settled_contracts:
        contract_id = settled_contract.xpath(
            "cbc:ID[@schemeName='contract']/text()", namespaces=namespaces
        )

        if contract_id:
            contract = {"id": contract_id[0]}
            result["contracts"].append(contract)

    return result if result["contracts"] else None


def merge_contract_technical_identifier(
    release_json: dict[str, Any],
    contract_technical_identifier_data: dict[str, Any] | None,
) -> None:
    """
    Merge contract technical identifier data into the release JSON.

    Args:
        release_json: Target release JSON to update
        contract_technical_identifier_data: Contract data containing identifiers

    Effects:
        Updates the contracts section of release_json with new contracts,
        skipping any that already exist
    """
    if not contract_technical_identifier_data:
        logger.info("No Contract Technical Identifier data to merge.")
        return

    contracts = release_json.setdefault("contracts", [])

    for new_contract in contract_technical_identifier_data["contracts"]:
        if not any(contract["id"] == new_contract["id"] for contract in contracts):
            contracts.append(new_contract)

    logger.info(
        "Merged Contract Technical Identifier data for %d contracts.",
        len(contract_technical_identifier_data["contracts"]),
    )
