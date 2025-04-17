import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)

# BT-144: Not Awarded Reason
# TED XPaths:
# - TED_EXPORT/FORM_SECTION/F03_2014/AWARD_CONTRACT/NO_AWARDED_CONTRACT/PROCUREMENT_UNSUCCESSFUL
# - TED_EXPORT/FORM_SECTION/F03_2014/AWARD_CONTRACT/NO_AWARDED_CONTRACT/PROCUREMENT_DISCONTINUED
# - (Similar patterns for F13, F21, F22, F23, F25)
# OCDS Mapping: awards[].status, awards[].statusDetails

# Mapping for decision reason codes - from authority table
REASON_CODE_MAPPING = {
    "all-rej": "All tenders, requests to participate or projects were withdrawn or found inadmissible",
    "chan-need": "Decision of the buyer, because of a change in needs",
    "ins-fund": "Decision of the buyer, because of insufficient funds",
    "no-rece": "No tenders, requests to participate or projects were received",
    "no-signed": "The highest ranked tenderer(s) refused to sign the contract",
    "none-rej": "No tenders or requests to participate were received or all were rejected",
    "one-admis": "Only one admissible tender, request to participate or project was received",
    "other": "Other",
    "rev-body": "Decision of a review body or another judicial body",
    "rev-buyer": "Decision of the buyer following a tenderer's request to review the award",
    "tch-pr-error": "Decision of the buyer, not following a tenderer's request to review the award, because of technical or procedural errors",
}


def parse_not_awarded_reason(xml_content: str | bytes) -> dict[str, Any] | None:
    """
    Parse the not awarded reason from TED XML.

    Args:
        xml_content: The TED XML content as string or bytes.

    Returns:
        A dictionary containing award information, or None if no data found
        The structure follows:
        {
            "awards": [
                {
                    "id": str,
                    "status": "unsuccessful",
                    "statusDetails": str,
                    "relatedLots": [str]
                }
            ]
        }
    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")

    try:
        root = etree.fromstring(xml_content)

        result = {"awards": []}

        # Check various forms with no awarded contract information
        forms_to_check = [
            "F03_2014",
            "F13_2014",
            "F21_2014",
            "F22_2014",
            "F23_2014",
            "F25_2014",
        ]

        for form_name in forms_to_check:
            # Handle standard contract forms
            if form_name != "F13_2014":
                base_path = f"FORM_SECTION/{form_name}/AWARD_CONTRACT"
                no_awarded_contracts = root.xpath(
                    f"{base_path}/*[contains(name(),'NO_AWARDED_CONTRACT')]"
                )
            else:
                # Handle prize results (F13)
                base_path = f"FORM_SECTION/{form_name}/RESULTS"
                no_awarded_contracts = root.xpath(
                    f"{base_path}/*[contains(name(),'NO_AWARDED_PRIZE')]"
                )

            for i, contract in enumerate(no_awarded_contracts):
                lot_id = contract.getparent().xpath("LOT_NO/text()")

                # Check for unsuccessful procurement
                procurement_unsuccessful = contract.xpath(
                    "PROCUREMENT_UNSUCCESSFUL/text()"
                )
                if (
                    procurement_unsuccessful
                    and procurement_unsuccessful[0].strip().lower() == "true"
                ):
                    reason_code = "no-rece"  # Most common case for unsuccessful
                    status_details = REASON_CODE_MAPPING.get(reason_code, "Unknown")
                else:
                    # Check for discontinued procurement
                    procurement_discontinued = contract.xpath(
                        "PROCUREMENT_DISCONTINUED/text()"
                    )
                    if not (
                        procurement_discontinued
                        and procurement_discontinued[0].strip().lower() == "true"
                    ):
                        continue
                    reason_code = "chan-need"  # Most common case for discontinued
                    status_details = REASON_CODE_MAPPING.get(reason_code, "Unknown")

                # Generate result ID
                result_id = f"RES-{i + 1:04d}"

                # Create award entry
                if lot_id:
                    award = {
                        "id": result_id,
                        "status": "unsuccessful",
                        "statusDetails": status_details,
                        "relatedLots": [lot_id[0].strip()],
                    }
                    result["awards"].append(award)

        return result if result["awards"] else None

    except Exception as e:
        logger.warning("Error parsing not awarded reason: %s", e)

    return None


def merge_not_awarded_reason(
    release_json: dict[str, Any], parsed_data: dict[str, Any] | None
) -> None:
    """
    Merge the parsed not awarded reason data into the release JSON.

    Args:
        release_json: The release JSON to merge into.
        parsed_data: The parsed data from parse_not_awarded_reason.
    """
    if not parsed_data:
        logger.info("No not awarded reason data to merge.")
        return

    existing_awards = release_json.setdefault("awards", [])

    for new_award in parsed_data["awards"]:
        # Try to find existing award with the same ID
        existing_award = next(
            (a for a in existing_awards if a.get("id") == new_award["id"]), None
        )

        if existing_award:
            # Update existing award
            existing_award.update(new_award)
        else:
            # Add new award
            existing_awards.append(new_award)

    logger.info(
        "Merged not awarded reason data for %d awards", len(parsed_data["awards"])
    )
