import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)

# BT-18: Submission URL
# TED XPaths:
# - TED_EXPORT/FORM_SECTION/F01_2014/CONTRACTING_BODY/ADDRESS_PARTICIPATION
# - TED_EXPORT/FORM_SECTION/F02_2014/CONTRACTING_BODY/ADDRESS_PARTICIPATION
# - TED_EXPORT/FORM_SECTION/F04_2014/CONTRACTING_BODY/ADDRESS_PARTICIPATION
# - TED_EXPORT/FORM_SECTION/F05_2014/CONTRACTING_BODY/ADDRESS_PARTICIPATION
# - TED_EXPORT/FORM_SECTION/F07_2014/CONTRACTING_BODY/ADDRESS_PARTICIPATION
# - TED_EXPORT/FORM_SECTION/F12_2014/CONTRACTING_BODY/ADDRESS_PARTICIPATION
# OCDS Mapping: tender.lots[].submissionMethodDetails


def parse_submission_url(
    xml_content: str | bytes,
) -> dict[str, Any] | None:
    """Parses the submission URL from TED XML content.

    Args:
        xml_content (Union[str, bytes]): The XML content to parse.

    Returns:
        Optional[Dict[str, Any]]: A dictionary containing submission URL data,
        or None if no data is found.
    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")

    result = None

    try:
        root = etree.fromstring(xml_content)
        temp_result = {"tender": {"lots": []}}

        # Forms to check for submission URL
        forms_to_check = [
            "F01_2014",
            "F02_2014",
            "F04_2014",
            "F05_2014",
            "F07_2014",
            "F12_2014",
        ]

        for form_name in forms_to_check:
            # Check if submission URL is provided
            address_participation = root.xpath(
                f"FORM_SECTION/{form_name}/CONTRACTING_BODY/ADDRESS_PARTICIPATION/text()"
            )

            if address_participation:
                submission_url = address_participation[0].strip()
                
                # Check for lots
                lots = root.xpath(f"FORM_SECTION/{form_name}//LOT_NO/text()")

                if lots:
                    # If lots are defined, associate the URL with each lot
                    for lot_id in lots:
                        lot_data = {
                            "id": lot_id.strip(),
                            "submissionMethodDetails": submission_url,
                        }
                        temp_result["tender"]["lots"].append(lot_data)
                else:
                    # If no lots are defined, create a default lot
                    lot_data = {
                        "id": "1",  # Default lot ID
                        "submissionMethodDetails": submission_url,
                    }
                    temp_result["tender"]["lots"].append(lot_data)

                logger.info(
                    "Found submission URL for %d lots",
                    len(temp_result["tender"]["lots"]),
                )
                result = temp_result
                break

    except Exception:
        logger.exception("Error parsing submission URL")
        result = None

    return result


def merge_submission_url(
    release_json: dict[str, Any],
    submission_url_data: dict[str, Any] | None,
) -> None:
    """Merges the submission URL data into the given release JSON.

    Args:
        release_json (Dict[str, Any]): The release JSON to merge data into.
        submission_url_data (Optional[Dict[str, Any]]): The submission URL data to merge.

    Returns:
        None
    """
    if not submission_url_data:
        logger.info("No Submission URL data to merge")
        return

    existing_lots = release_json.setdefault("tender", {}).setdefault("lots", [])

    for new_lot in submission_url_data["tender"]["lots"]:
        existing_lot = next(
            (lot for lot in existing_lots if lot["id"] == new_lot["id"]),
            None,
        )

        if existing_lot:
            existing_lot.update({"submissionMethodDetails": new_lot["submissionMethodDetails"]})
        else:
            existing_lots.append(new_lot)

    logger.info(
        "Merged Submission URL data for %d lots",
        len(submission_url_data["tender"]["lots"]),
    )
