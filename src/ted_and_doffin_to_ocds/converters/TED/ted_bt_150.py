import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)

# BT-150: Contract Identifier
# TED XPaths:
# - TED_EXPORT/FORM_SECTION/F03_2014/AWARD_CONTRACT/CONTRACT_NO
# - TED_EXPORT/FORM_SECTION/F15_2014/AWARD_CONTRACT/CONTRACT_NO
# - TED_EXPORT/FORM_SECTION/F20_2014/AWARD_CONTRACT/CONTRACT_NO
# - TED_EXPORT/FORM_SECTION/F21_2014/AWARD_CONTRACT/CONTRACT_NO
# - TED_EXPORT/FORM_SECTION/F22_2014/AWARD_CONTRACT/CONTRACT_NO
# OCDS Mapping: contracts[].id, contracts[].identifiers, contracts[].awardID


def parse_contract_identifier(
    xml_content: str | bytes,
) -> dict[str, list[dict[str, Any]]] | None:
    """Parses contract identifiers from TED XML content.

    Args:
        xml_content (Union[str, bytes]): The XML content to parse.

    Returns:
        Optional[Dict[str, List[Dict[str, Any]]]]: A dictionary containing contract identifiers,
        or None if no contracts are found.
    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")

    try:
        root = etree.fromstring(xml_content)
        result = {"contracts": []}

        # List of forms to check
        forms_to_check = ["F03_2014", "F15_2014", "F20_2014", "F21_2014", "F22_2014"]

        for form_name in forms_to_check:
            award_contracts = root.xpath(f"FORM_SECTION/{form_name}/AWARD_CONTRACT")

            for i, contract_section in enumerate(award_contracts):
                # Check if contract was awarded
                awarded_contract = contract_section.xpath("AWARDED_CONTRACT")
                if not awarded_contract:
                    continue

                # Get contract number/identifier
                contract_no = contract_section.xpath("CONTRACT_NO/text()")

                # If no explicit contract number is provided, generate one based on guidance
                if not contract_no:
                    # Get notice number (if available)
                    notice_number = root.xpath(
                        "CODED_DATA_SECTION/NOTICE_DATA/NO_DOC_OJS/text()"
                    )
                    item_attr = contract_section.get("ITEM", str(i + 1))

                    if notice_number:
                        contract_no = [f"{notice_number[0]}-{item_attr}"]
                    else:
                        contract_no = [f"CON-{i + 1:04d}"]

                contract_id = contract_no[0].strip()

                # Generate award ID (based on same pattern used in other converters)
                award_id = f"RES-{i + 1:04d}"

                contract = {
                    "id": contract_id,
                    "identifiers": [
                        {
                            "id": contract_id,
                            "scheme": "TED",  # Using TED as the scheme for legacy notices
                        }
                    ],
                    "awardID": award_id,
                }

                result["contracts"].append(contract)
                logger.info(
                    "Found contract %s linked to award %s",
                    contract_id,
                    award_id,
                )

        return result if result["contracts"] else None

    except Exception:
        logger.exception("Error parsing contract identifiers")
        return None


def merge_contract_identifier(
    release_json: dict[str, Any],
    contract_identifier_data: dict[str, list[dict[str, Any]]] | None,
) -> None:
    """Merges the contract identifier data into the given release JSON.

    Args:
        release_json (Dict[str, Any]): The release JSON to merge data into.
        contract_identifier_data (Optional[Dict[str, List[Dict[str, Any]]]]):
            The contract identifier data to merge.

    Returns:
        None
    """
    if not contract_identifier_data:
        logger.info("No Contract Identifier data to merge")
        return

    existing_contracts = release_json.setdefault("contracts", [])

    for new_contract in contract_identifier_data["contracts"]:
        existing_contract = next(
            (
                contract
                for contract in existing_contracts
                if contract["id"] == new_contract["id"]
            ),
            None,
        )

        if existing_contract:
            # Ensure identifiers array exists
            if "identifiers" not in existing_contract:
                existing_contract["identifiers"] = []

            # Add new identifiers avoiding duplicates
            existing_identifiers = {
                (i["id"], i.get("scheme")) for i in existing_contract["identifiers"]
            }

            for new_identifier in new_contract["identifiers"]:
                if (
                    new_identifier["id"],
                    new_identifier.get("scheme"),
                ) not in existing_identifiers:
                    existing_contract["identifiers"].append(new_identifier)

            # Set awardID if not already set
            if "awardID" not in existing_contract and "awardID" in new_contract:
                existing_contract["awardID"] = new_contract["awardID"]
        else:
            existing_contracts.append(new_contract)

    logger.info(
        "Merged Contract Identifier data for %d contracts",
        len(contract_identifier_data["contracts"]),
    )
    logger.debug(
        "Release JSON after merging Contract Identifier data: %s", release_json
    )
