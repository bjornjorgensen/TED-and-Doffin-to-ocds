import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)

# BT-17: Submission Electronic
# TED XPaths:
# - TED_EXPORT/FORM_SECTION/F01_2014/CONTRACTING_BODY/URL_PARTICIPATION
# - TED_EXPORT/FORM_SECTION/F02_2014/CONTRACTING_BODY/URL_PARTICIPATION
# - TED_EXPORT/FORM_SECTION/F04_2014/CONTRACTING_BODY/URL_PARTICIPATION
# - TED_EXPORT/FORM_SECTION/F05_2014/CONTRACTING_BODY/URL_PARTICIPATION
# - TED_EXPORT/FORM_SECTION/F07_2014/CONTRACTING_BODY/URL_PARTICIPATION
# - TED_EXPORT/FORM_SECTION/F12_2014/CONTRACTING_BODY/URL_PARTICIPATION
# - TED_EXPORT/FORM_SECTION/F21_2014/CONTRACTING_BODY/URL_PARTICIPATION
# - TED_EXPORT/FORM_SECTION/F22_2014/CONTRACTING_BODY/URL_PARTICIPATION
# - TED_EXPORT/FORM_SECTION/F24_2014/CONTRACTING_BODY/URL_PARTICIPATION
# OCDS Mapping: tender.lots[].submissionTerms.electronicSubmissionPolicy


def parse_submission_electronic(
    xml_content: str | bytes,
) -> dict[str, Any] | None:
    """Parses the electronic submission policy from TED XML content.

    Args:
        xml_content (Union[str, bytes]): The XML content to parse.

    Returns:
        Optional[Dict[str, Any]]: A dictionary containing electronic submission policy data,
        or None if no data is found.
    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")

    result = None

    try:
        root = etree.fromstring(xml_content)
        temp_result = {"tender": {"lots": []}}

        # Forms to check for electronic submission
        forms_to_check = [
            "F01_2014",
            "F02_2014",
            "F04_2014",
            "F05_2014",
            "F07_2014",
            "F12_2014",
            "F21_2014",
            "F22_2014",
            "F24_2014",
        ]

        for form_name in forms_to_check:
            # Check if electronic submission URLs are provided
            url_participation = root.xpath(
                f"FORM_SECTION/{form_name}/CONTRACTING_BODY/URL_PARTICIPATION/text()"
            )

            if url_participation:
                # If a URL is provided, electronic submission is allowed or required
                # In TED format, we can't always distinguish between allowed and required
                # Default to "allowed" as the safest option
                policy_value = "allowed"

                # Check for lots
                lots = root.xpath(f"FORM_SECTION/{form_name}//LOT_NO/text()")

                if lots:
                    # If lots are defined, associate the policy with each lot
                    for lot_id in lots:
                        lot_data = {
                            "id": lot_id.strip(),
                            "submissionTerms": {
                                "electronicSubmissionPolicy": policy_value
                            },
                        }
                        temp_result["tender"]["lots"].append(lot_data)
                else:
                    # If no lots are defined, create a default lot
                    lot_data = {
                        "id": "1",  # Default lot ID
                        "submissionTerms": {"electronicSubmissionPolicy": policy_value},
                    }
                    temp_result["tender"]["lots"].append(lot_data)

                logger.info(
                    "Found electronic submission policy '%s' for %d lots",
                    policy_value,
                    len(temp_result["tender"]["lots"]),
                )
                result = temp_result
                break

    except Exception:
        logger.exception("Error parsing electronic submission policy")
        result = None

    return result


def merge_submission_electronic(
    release_json: dict[str, Any],
    submission_electronic_data: dict[str, Any] | None,
) -> None:
    """Merges the electronic submission policy data into the given release JSON.

    Args:
        release_json (Dict[str, Any]): The release JSON to merge data into.
        submission_electronic_data (Optional[Dict[str, Any]]): The submission policy data to merge.

    Returns:
        None
    """
    if not submission_electronic_data:
        logger.info("No Electronic Submission Policy data to merge")
        return

    existing_lots = release_json.setdefault("tender", {}).setdefault("lots", [])

    for new_lot in submission_electronic_data["tender"]["lots"]:
        existing_lot = next(
            (lot for lot in existing_lots if lot["id"] == new_lot["id"]),
            None,
        )

        if existing_lot:
            existing_lot.setdefault("submissionTerms", {}).update(
                new_lot["submissionTerms"]
            )
        else:
            existing_lots.append(new_lot)

    logger.info(
        "Merged Electronic Submission Policy data for %d lots",
        len(submission_electronic_data["tender"]["lots"]),
    )
