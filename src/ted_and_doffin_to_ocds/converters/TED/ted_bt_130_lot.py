import logging
from typing import Any

from lxml import etree

from ted_and_doffin_to_ocds.utils.date_utils import start_date

logger = logging.getLogger(__name__)

# BT-130: Dispatch Invitation Tender Date
# TED XPaths:
# - TED_EXPORT/FORM_SECTION/F02_2014/PROCEDURE/DATE_DISPATCH_INVITATIONS
# - TED_EXPORT/FORM_SECTION/F04_2014/PROCEDURE/DATE_RECEIPT_TENDERS
# - TED_EXPORT/FORM_SECTION/F05_2014/PROCEDURE/DATE_DISPATCH_INVITATIONS
# - TED_EXPORT/FORM_SECTION/F12_2014/PROCEDURE/DATE_DISPATCH_INVITATIONS
# - TED_EXPORT/FORM_SECTION/CONTRACT_DEFENCE/FD_CONTRACT_DEFENCE/PROCEDURE_DEFINITION_CONTRACT_NOTICE_DEFENCE/ADMINISTRATIVE_INFORMATION_CONTRACT_NOTICE_DEFENCE/DISPATCH_INVITATIONS_DATE
# - TED_EXPORT/FORM_SECTION/CONTRACT_CONCESSIONAIRE_DEFENCE/FD_CONTRACT_CONCESSIONAIRE_DEFENCE/PROCEDURE_DEFINITION_CONTRACT_SUB_DEFENCE/ADMINISTRATIVE_INFORMATION_CONTRACT_SUB_NOTICE_DEFENCE/DISPATCH_INVITATIONS_DATE
# OCDS Mapping: tender.secondStage.invitationDate, tender.tenderPeriod.endDate


def parse_dispatch_invitation_tender_date(
    root: etree._Element, namespaces: dict[str, str]
) -> dict[str, Any] | None:
    """
    Parse the dispatch invitation tender date from TED XML.

    Args:
        root: The root element of the TED XML document.
        namespaces: The XML namespaces.

    Returns:
        A dictionary containing tender.secondStage.invitationDate and tender.tenderPeriod.endDate,
        or None if not found.
        Example: {"tender": {"secondStage": {"invitationDate": "2019-11-15T00:00:00+01:00"},
                             "tenderPeriod": {"endDate": "2019-11-15T00:00:00+01:00"}}}
    """
    date_xpaths = [
        "FORM_SECTION/F02_2014/PROCEDURE/DATE_DISPATCH_INVITATIONS/text()",
        "FORM_SECTION/F04_2014/PROCEDURE/DATE_RECEIPT_TENDERS/text()",
        "FORM_SECTION/F05_2014/PROCEDURE/DATE_DISPATCH_INVITATIONS/text()",
        "FORM_SECTION/F12_2014/PROCEDURE/DATE_DISPATCH_INVITATIONS/text()",
        "FORM_SECTION/CONTRACT_DEFENCE/FD_CONTRACT_DEFENCE/PROCEDURE_DEFINITION_CONTRACT_NOTICE_DEFENCE/ADMINISTRATIVE_INFORMATION_CONTRACT_NOTICE_DEFENCE/DISPATCH_INVITATIONS_DATE/text()",
        "FORM_SECTION/CONTRACT_CONCESSIONAIRE_DEFENCE/FD_CONTRACT_CONCESSIONAIRE_DEFENCE/PROCEDURE_DEFINITION_CONTRACT_SUB_DEFENCE/ADMINISTRATIVE_INFORMATION_CONTRACT_SUB_NOTICE_DEFENCE/DISPATCH_INVITATIONS_DATE/text()",
    ]

    date_str = None
    for xpath in date_xpaths:
        result = root.xpath(xpath, namespaces=namespaces)
        if result:
            date_str = result[0]
            break

    if date_str:
        try:
            iso_date = start_date(date_str)
        except ValueError as e:
            logger.warning(
                "Error parsing dispatch invitation tender date '%s': %s", date_str, e
            )
        else:
            return {
                "tender": {
                    "secondStage": {"invitationDate": iso_date},
                    "tenderPeriod": {"endDate": iso_date},
                }
            }
    return None


def merge_dispatch_invitation_tender_date(
    release_json: dict[str, Any], parsed_data: dict[str, Any] | None
) -> None:
    """
    Merge the parsed dispatch invitation tender date into the release JSON.

    Args:
        release_json: The release JSON to merge into.
        parsed_data: The parsed data dictionary from parse_dispatch_invitation_tender_date.
    """
    if parsed_data and "tender" in parsed_data:
        tender = release_json.setdefault("tender", {})

        # Update secondStage.invitationDate
        if "secondStage" in parsed_data["tender"]:
            second_stage = tender.setdefault("secondStage", {})
            second_stage.update(parsed_data["tender"]["secondStage"])

        # Update tenderPeriod.endDate
        if "tenderPeriod" in parsed_data["tender"]:
            tender_period = tender.setdefault("tenderPeriod", {})
            tender_period.update(parsed_data["tender"]["tenderPeriod"])

        logger.info("Merged dispatch invitation tender date.")
    else:
        logger.info("No dispatch invitation tender date found to merge.")
