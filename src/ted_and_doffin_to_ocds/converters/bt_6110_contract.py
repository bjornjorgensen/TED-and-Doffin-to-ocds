# converters/bt_6110_Contract.py

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


def parse_contract_eu_funds_details(xml_content: str | bytes) -> dict[str, Any] | None:
    """
    Parse the XML content to extract contract EU funds details (BT-6110).

    Gets funding information from each contract. Creates/updates corresponding Finance
    objects in the contract's finance array with funding descriptions.

    Args:
        xml_content: XML content as string or bytes containing procurement data

    Returns:
        Dictionary containing contracts with funding details or None if no data found
    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")

    try:
        root = etree.fromstring(xml_content)
        result = {"contracts": []}

        settled_contracts = root.xpath(
            "//ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/"
            "efext:EformsExtension/efac:NoticeResult/efac:SettledContract",
            namespaces=NAMESPACES,
        )

        for contract in settled_contracts:
            try:
                contract_id = contract.xpath(
                    "cbc:ID[@schemeName='contract']/text()",
                    namespaces=NAMESPACES,
                )[0]

                funding_descriptions = contract.xpath(
                    "efac:Funding/cbc:FundingProgram/text()",
                    namespaces=NAMESPACES,
                )

                if contract_id and funding_descriptions:
                    contract_data = {
                        "id": contract_id,
                        "finance": [
                            {"description": desc} for desc in funding_descriptions
                        ],
                    }

                    # Find corresponding LotResult to get awardID
                    award_id = root.xpath(
                        f"//efac:NoticeResult/efac:LotResult[efac:SettledContract/cbc:ID"
                        f"[@schemeName='contract']/text()='{contract_id}']/"
                        "cbc:ID[@schemeName='result']/text()",
                        namespaces=NAMESPACES,
                    )
                    if award_id:
                        contract_data["awardID"] = award_id[0]

                    result["contracts"].append(contract_data)

            except (IndexError, AttributeError) as e:
                logger.warning("Skipping incomplete contract data: %s", e)
                continue

        if result["contracts"]:
            return result

    except Exception:
        logger.exception("Error parsing contract EU funds details")
        return None

    return None


def merge_contract_eu_funds_details(
    release_json: dict[str, Any], eu_funds_details: dict[str, Any] | None
) -> None:
    """
    Merge EU funds details into the release JSON.

    Updates or creates contracts with funding information.
    Preserves existing contract data while adding/updating finance details.

    Args:
        release_json: The target release JSON to update
        eu_funds_details: The source data containing EU funds details to merge

    Returns:
        None
    """
    if not eu_funds_details:
        logger.warning("BT-6110-Contract: No contract EU funds details to merge")
        return

    existing_contracts = release_json.setdefault("contracts", [])

    for new_contract in eu_funds_details["contracts"]:
        existing_contract = next(
            (
                contract
                for contract in existing_contracts
                if contract["id"] == new_contract["id"]
            ),
            None,
        )
        if existing_contract:
            existing_contract.setdefault("finance", []).extend(new_contract["finance"])
            if "awardID" in new_contract:
                existing_contract["awardID"] = new_contract["awardID"]
        else:
            existing_contracts.append(new_contract)

    logger.info(
        "BT-6110-Contract: Merged contract EU funds details for %d contracts",
        len(eu_funds_details["contracts"]),
    )
