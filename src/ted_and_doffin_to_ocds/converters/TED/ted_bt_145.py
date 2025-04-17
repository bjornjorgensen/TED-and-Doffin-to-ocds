import logging
from typing import Any

from lxml import etree

from ted_and_doffin_to_ocds.utils.date_utils import end_date

logger = logging.getLogger(__name__)

# BT-145: Contract Conclusion Date
# TED XPaths:
# - TED_EXPORT/FORM_SECTION/F03_2014/AWARD_CONTRACT/AWARDED_CONTRACT/DATE_CONCLUSION_CONTRACT
# - TED_EXPORT/FORM_SECTION/F21_2014/AWARD_CONTRACT/AWARDED_CONTRACT/DATE_CONCLUSION_CONTRACT
# - TED_EXPORT/FORM_SECTION/F22_2014/AWARD_CONTRACT/AWARDED_CONTRACT/DATE_CONCLUSION_CONTRACT
# - TED_EXPORT/FORM_SECTION/F23_2014/AWARD_CONTRACT/AWARDED_CONTRACT/DATE_CONCLUSION_CONTRACT
# - TED_EXPORT/FORM_SECTION/F25_2014/AWARD_CONTRACT/AWARDED_CONTRACT/DATE_CONCLUSION_CONTRACT
# OCDS Mapping: contracts[].dateSigned


def parse_contract_conclusion_date(
    xml_content: str | bytes,
) -> dict[str, list[dict[str, Any]]] | None:
    """Parses the contract conclusion date from TED XML content.

    Args:
        xml_content (Union[str, bytes]): The XML content to parse.

    Returns:
        Optional[Dict[str, List[Dict[str, Any]]]]: A dictionary containing contract conclusion dates,
        or None if no contracts are found.
    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")

    try:
        root = etree.fromstring(xml_content)
        result = {"contracts": []}

        # List of forms to check
        forms_to_check = ["F03_2014", "F21_2014", "F22_2014", "F23_2014", "F25_2014"]

        for form_name in forms_to_check:
            award_contracts = root.xpath(f"FORM_SECTION/{form_name}/AWARD_CONTRACT")

            for i, contract_section in enumerate(award_contracts):
                # Check if contract was awarded
                awarded_contract = contract_section.xpath("AWARDED_CONTRACT")
                if not awarded_contract:
                    continue

                # Get contract conclusion date
                date_conclusion = contract_section.xpath(
                    "AWARDED_CONTRACT/DATE_CONCLUSION_CONTRACT/text()"
                )

                if not date_conclusion:
                    continue

                conclusion_date = date_conclusion[0].strip()

                # Get lot ID to link to award
                lot_id = contract_section.xpath("LOT_NO/text()")
                lot_id = lot_id[0].strip() if lot_id else None

                # Generate contract ID
                contract_id = f"CON-{i + 1:04d}"

                # Generate award ID (based on same pattern used in other converters)
                award_id = f"RES-{i + 1:04d}"

                contract = {
                    "id": contract_id,
                    "dateSigned": end_date(conclusion_date),
                    "awardID": award_id,
                }

                result["contracts"].append(contract)
                logger.info(
                    "Found contract %s with date %s linked to award %s",
                    contract_id,
                    conclusion_date,
                    award_id,
                )

        return result if result["contracts"] else None

    except Exception:
        logger.exception("Error parsing contract conclusion date")
        return None


def merge_contract_conclusion_date(
    release_json: dict[str, Any],
    contract_conclusion_date_data: dict[str, list[dict[str, Any]]] | None,
) -> None:
    """Merges the contract conclusion date data into the given release JSON.

    Args:
        release_json (Dict[str, Any]): The release JSON to merge data into.
        contract_conclusion_date_data (Optional[Dict[str, List[Dict[str, Any]]]]):
            The contract conclusion date data to merge.

    Returns:
        None
    """
    if not contract_conclusion_date_data:
        logger.info("No Contract Conclusion Date data to merge")
        return

    existing_contracts = release_json.setdefault("contracts", [])

    for new_contract in contract_conclusion_date_data["contracts"]:
        existing_contract = next(
            (
                contract
                for contract in existing_contracts
                if contract["id"] == new_contract["id"]
            ),
            None,
        )

        if existing_contract:
            existing_contract["dateSigned"] = new_contract["dateSigned"]
            if "awardID" not in existing_contract and "awardID" in new_contract:
                existing_contract["awardID"] = new_contract["awardID"]
        else:
            existing_contracts.append(new_contract)

    logger.info(
        "Merged Contract Conclusion Date data for %d contracts",
        len(contract_conclusion_date_data["contracts"]),
    )
