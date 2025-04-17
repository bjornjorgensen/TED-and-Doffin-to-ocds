import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)

# BT-160: Concession Revenue Buyer
# TED XPaths:
# - TED_EXPORT/FORM_SECTION/F23_2014/AWARD_CONTRACT/AWARDED_CONTRACT/VAL_PRICE_PAYMENT
# OCDS Mapping: contracts[].implementation.charges

GOVERNMENT_CHARGE_TITLE = "Prizes, payments or other financial advantages provided by the contracting authority/entity"


def parse_concession_revenue_buyer(
    xml_content: str | bytes,
) -> dict[str, list[dict[str, Any]]] | None:
    """Parses concession revenue buyer information from TED XML content.

    Args:
        xml_content (Union[str, bytes]): The XML content to parse.

    Returns:
        Optional[Dict[str, List[Dict[str, Any]]]]: A dictionary containing concession revenue data,
        or None if no data is found.
    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")

    try:
        root = etree.fromstring(xml_content)
        result = {"contracts": []}

        # Check for F23_2014 form
        award_contracts = root.xpath("FORM_SECTION/F23_2014/AWARD_CONTRACT")

        for i, contract_section in enumerate(award_contracts):
            # Check if contract was awarded
            awarded_contract = contract_section.xpath("AWARDED_CONTRACT")
            if not awarded_contract:
                continue

            # Get contract price payment value
            val_price_payment = contract_section.xpath(
                "AWARDED_CONTRACT/VAL_PRICE_PAYMENT/text()"
            )
            if not val_price_payment:
                continue

            try:
                price_value = float(val_price_payment[0].strip())
            except (ValueError, TypeError):
                logger.warning(
                    "Invalid value format for concession revenue: %s",
                    val_price_payment[0] if val_price_payment else "None",
                )
                continue

            # Get currency
            currency = contract_section.xpath(
                "AWARDED_CONTRACT/VAL_PRICE_PAYMENT/@CURRENCY"
            )
            currency_code = (
                currency[0] if currency else "EUR"
            )  # Default to EUR if not specified

            # Generate contract ID
            contract_id = f"CON-{i + 1:04d}"

            # Generate award ID (based on same pattern used in other converters)
            award_id = f"RES-{i + 1:04d}"

            contract = {
                "id": contract_id,
                "awardID": award_id,
                "implementation": {
                    "charges": [
                        {
                            "id": "government",
                            "title": GOVERNMENT_CHARGE_TITLE,
                            "estimatedValue": {
                                "amount": price_value,
                                "currency": currency_code,
                            },
                            "paidBy": "government",
                        }
                    ]
                },
            }

            result["contracts"].append(contract)
            logger.info(
                "Found concession revenue %s for contract %s linked to award %s",
                price_value,
                contract_id,
                award_id,
            )

        return result if result["contracts"] else None

    except Exception:
        logger.exception("Error parsing concession revenue buyer")
        return None


def merge_concession_revenue_buyer(
    release_json: dict[str, Any],
    concession_revenue_data: dict[str, list[dict[str, Any]]] | None,
) -> None:
    """Merges the concession revenue buyer data into the given release JSON.

    Args:
        release_json (Dict[str, Any]): The release JSON to merge data into.
        concession_revenue_data (Optional[Dict[str, List[Dict[str, Any]]]]):
            The concession revenue data to merge.

    Returns:
        None
    """
    if not concession_revenue_data:
        logger.info("No Concession Revenue Buyer data to merge")
        return

    existing_contracts = release_json.setdefault("contracts", [])

    for new_contract in concession_revenue_data["contracts"]:
        existing_contract = next(
            (
                contract
                for contract in existing_contracts
                if contract["id"] == new_contract["id"]
            ),
            None,
        )

        if existing_contract:
            # Ensure implementation and charges arrays exist
            existing_implementation = existing_contract.setdefault("implementation", {})
            existing_charges = existing_implementation.setdefault("charges", [])

            # Add the new charge
            existing_charges.extend(new_contract["implementation"]["charges"])

            # Add award ID if not present
            if "awardID" not in existing_contract and "awardID" in new_contract:
                existing_contract["awardID"] = new_contract["awardID"]
        else:
            existing_contracts.append(new_contract)

    logger.info(
        "Merged Concession Revenue Buyer data for %d contracts",
        len(concession_revenue_data["contracts"]),
    )
