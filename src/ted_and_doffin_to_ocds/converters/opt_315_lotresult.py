# converters/opt_315_lotresult.py

import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)


def parse_contract_identifier_reference(
    xml_content: str | bytes,
) -> dict[str, Any] | None:
    """
    Parse contract identifier references from lot results.

    For each lot result:
    - Gets contract ID from SettledContract
    - Links contracts to their awards through awardID

    Args:
        xml_content: XML content containing lot result data

    Returns:
        Optional[Dict]: Dictionary containing contracts with award references, or None if no data.
        Example structure:
        {
            "contracts": [
                {
                    "id": "contract_id",
                    "awardID": "award_id"
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

    # Parse LotResult information
    lot_results = root.xpath(
        "//efac:NoticeResult/efac:LotResult", namespaces=namespaces
    )

    for lot_result in lot_results:
        result_id = lot_result.xpath(
            "cbc:ID[@schemeName='result']/text()", namespaces=namespaces
        )
        contract_id = lot_result.xpath(
            "efac:SettledContract/cbc:ID[@schemeName='contract']/text()",
            namespaces=namespaces,
        )

        if result_id and contract_id:
            contract = {"id": contract_id[0], "awardID": result_id[0]}
            result["contracts"].append(contract)

    return result if result["contracts"] else None


def merge_contract_identifier_reference(
    release_json: dict[str, Any], contract_identifier_data: dict[str, Any] | None
) -> None:
    """
    Merge contract identifier data into the release JSON.

    Args:
        release_json: Target release JSON to update
        contract_identifier_data: Contract data containing identifiers and award references

    Effects:
        Updates the contracts section of release_json with contract IDs
        and their award references
    """
    if not contract_identifier_data:
        logger.info("No Contract Identifier Reference data to merge.")
        return

    contracts = release_json.setdefault("contracts", [])

    for new_contract in contract_identifier_data["contracts"]:
        existing_contract = next(
            (
                contract
                for contract in contracts
                if contract["id"] == new_contract["id"]
            ),
            None,
        )
        if existing_contract:
            existing_contract["awardID"] = new_contract["awardID"]
        else:
            contracts.append(new_contract)

    logger.info(
        "Merged Contract Identifier Reference data for %d contracts.",
        len(contract_identifier_data["contracts"]),
    )
