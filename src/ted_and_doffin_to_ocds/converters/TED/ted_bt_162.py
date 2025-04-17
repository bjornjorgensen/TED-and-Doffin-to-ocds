import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)

# BT-162: Concession Revenue User
# TED XPaths:
# - TED_EXPORT/FORM_SECTION/F23_2014/AWARD_CONTRACT/AWARDED_CONTRACT/VAL_REVENUE
# OCDS Mapping: contracts[].implementation.charges (with id=user, paidBy=user)

USER_CHARGE_TITLE = "The estimated revenue coming from the users of the concession (e.g. fees and fines)."


def parse_concession_revenue_user(
    xml_content: str | bytes,
) -> dict[str, list[dict[str, Any]]] | None:
    """Parses user concession revenue from TED XML content.

    Args:
        xml_content (Union[str, bytes]): The XML content to parse.

    Returns:
        Optional[Dict[str, List[Dict[str, Any]]]]: A dictionary containing user concession revenue data,
        or None if no revenue data is found.
    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")

    try:
        root = etree.fromstring(xml_content)
        result = {"contracts": []}

        # Form F23_2014 contains concession revenue information
        award_contracts = root.xpath("FORM_SECTION/F23_2014/AWARD_CONTRACT")

        for i, contract_section in enumerate(award_contracts):
            # Check if contract was awarded
            awarded_contract = contract_section.xpath("AWARDED_CONTRACT")
            if not awarded_contract:
                continue

            # Get user revenue value
            revenue_values = contract_section.xpath(
                "AWARDED_CONTRACT/VAL_REVENUE/text()"
            )

            if not revenue_values:
                continue

            try:
                revenue_value = float(revenue_values[0].strip())

                # Get currency
                currency_path = "AWARDED_CONTRACT/VAL_REVENUE/@CURRENCY"
                currency = contract_section.xpath(currency_path)
                currency_code = (
                    currency[0] if currency else "EUR"
                )  # Default to EUR if not specified

                # Generate contract ID
                contract_id = f"CON-{i + 1:04d}"

                # Generate award ID
                award_id = f"RES-{i + 1:04d}"

                contract = {
                    "id": contract_id,
                    "awardID": award_id,
                    "implementation": {
                        "charges": [
                            {
                                "id": "user",
                                "title": USER_CHARGE_TITLE,
                                "estimatedValue": {
                                    "amount": revenue_value,
                                    "currency": currency_code,
                                },
                                "paidBy": "user",
                            }
                        ]
                    },
                }

                result["contracts"].append(contract)
                logger.info(
                    "Added user concession revenue to contract %s linked to award %s",
                    contract_id,
                    award_id,
                )

            except (ValueError, TypeError):
                logger.warning(
                    "Invalid value format for user concession revenue: %s",
                    revenue_values[0] if revenue_values else "None",
                )

        return result if result["contracts"] else None

    except Exception:
        logger.exception("Error parsing user concession revenue")
        return None


def merge_concession_revenue_user(
    release_json: dict[str, Any],
    concession_revenue_data: dict[str, list[dict[str, Any]]] | None,
) -> None:
    """Merges the user concession revenue data into the given release JSON.

    Args:
        release_json (Dict[str, Any]): The release JSON to merge data into.
        concession_revenue_data (Optional[Dict[str, List[Dict[str, Any]]]]):
            The user concession revenue data to merge.

    Returns:
        None
    """
    if not concession_revenue_data:
        logger.info("No User Concession Revenue data to merge")
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
            existing_implementation = existing_contract.setdefault("implementation", {})
            existing_charges = existing_implementation.setdefault("charges", [])
            existing_charges.extend(new_contract["implementation"]["charges"])

            if "awardID" not in existing_contract and "awardID" in new_contract:
                existing_contract["awardID"] = new_contract["awardID"]
        else:
            existing_contracts.append(new_contract)

    logger.info(
        "Merged User Concession Revenue data for %d contracts",
        len(concession_revenue_data["contracts"]),
    )
