import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)

# BT-161: Notice Value
# TED XPaths:
# - TED_EXPORT/FORM_SECTION/F20_2014/MODIFICATIONS_CONTRACT/DESCRIPTION_PROCUREMENT/VALUES/VAL_TOTAL
# - TED_EXPORT/FORM_SECTION/F23_2014/OBJECT_CONTRACT/VAL_TOTAL
# - TED_EXPORT/FORM_SECTION/F25_2014/OBJECT_CONTRACT/VAL_TOTAL
# OCDS Mapping: contracts[].value.amount


def parse_notice_value(
    xml_content: str | bytes,
) -> dict[str, list[dict[str, Any]]] | None:
    """Parses notice value from TED XML content.

    Args:
        xml_content (Union[str, bytes]): The XML content to parse.

    Returns:
        Optional[Dict[str, List[Dict[str, Any]]]]: A dictionary containing notice value data,
        or None if no notice value is found.
    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")

    try:
        root = etree.fromstring(xml_content)
        result = {"contracts": []}

        # Form types to check
        paths = [
            (
                "F20_2014",
                "MODIFICATIONS_CONTRACT/DESCRIPTION_PROCUREMENT/VALUES/VAL_TOTAL",
            ),
            ("F23_2014", "OBJECT_CONTRACT/VAL_TOTAL"),
            ("F25_2014", "OBJECT_CONTRACT/VAL_TOTAL"),
        ]

        for form_name, xpath in paths:
            total_values = root.xpath(f"FORM_SECTION/{form_name}/{xpath}/text()")

            if total_values:
                try:
                    total_value = float(total_values[0].strip())

                    # Get currency
                    currency_path = f"FORM_SECTION/{form_name}/{xpath}/@CURRENCY"
                    currency = root.xpath(currency_path)
                    currency_code = (
                        currency[0] if currency else "EUR"
                    )  # Default to EUR if not specified

                    # Check for existing contracts
                    award_contracts = root.xpath(
                        f"FORM_SECTION/{form_name}/AWARD_CONTRACT"
                    )

                    if award_contracts:
                        # If we have individual contracts, distribute the value among them
                        for i, contract_section in enumerate(award_contracts):
                            # Check if contract was awarded
                            awarded_contract = contract_section.xpath(
                                "AWARDED_CONTRACT"
                            )
                            if not awarded_contract:
                                continue

                            # Generate contract ID
                            contract_id = f"CON-{i + 1:04d}"

                            # Generate award ID (based on same pattern used in other converters)
                            award_id = f"RES-{i + 1:04d}"

                            contract = {
                                "id": contract_id,
                                "awardID": award_id,
                                "value": {
                                    "amount": total_value / len(award_contracts),
                                    "currency": currency_code,
                                },
                            }

                            result["contracts"].append(contract)
                            logger.info(
                                "Added notice value to contract %s linked to award %s",
                                contract_id,
                                award_id,
                            )
                    else:
                        # If no individual contracts, create a single contract
                        contract_id = "CON-0001"
                        award_id = "RES-0001"

                        contract = {
                            "id": contract_id,
                            "awardID": award_id,
                            "value": {
                                "amount": total_value,
                                "currency": currency_code,
                            },
                        }

                        result["contracts"].append(contract)
                        logger.info(
                            "Added notice value to contract %s linked to award %s",
                            contract_id,
                            award_id,
                        )

                    # Since we found a value, we can stop looking
                    break

                except (ValueError, TypeError):
                    logger.warning(
                        "Invalid value format for notice value: %s",
                        total_values[0] if total_values else "None",
                    )

        return result if result["contracts"] else None

    except Exception:
        logger.exception("Error parsing notice value")
        return None


def merge_notice_value(
    release_json: dict[str, Any],
    notice_value_data: dict[str, list[dict[str, Any]]] | None,
) -> None:
    """Merges the notice value data into the given release JSON.

    Args:
        release_json (Dict[str, Any]): The release JSON to merge data into.
        notice_value_data (Optional[Dict[str, List[Dict[str, Any]]]]):
            The notice value data to merge.

    Returns:
        None
    """
    if not notice_value_data:
        logger.info("No Notice Value data to merge")
        return

    existing_contracts = release_json.setdefault("contracts", [])

    for new_contract in notice_value_data["contracts"]:
        existing_contract = next(
            (
                contract
                for contract in existing_contracts
                if contract["id"] == new_contract["id"]
            ),
            None,
        )

        if existing_contract:
            # Update existing contract with value information
            existing_contract["value"] = new_contract["value"]

            # Add award ID if not present
            if "awardID" not in existing_contract and "awardID" in new_contract:
                existing_contract["awardID"] = new_contract["awardID"]
        else:
            existing_contracts.append(new_contract)

    logger.info(
        "Merged Notice Value data for %d contracts",
        len(notice_value_data["contracts"]),
    )
