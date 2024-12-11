# converters/bt_130_Lot.py

import logging

from lxml import etree

from ted_and_doffin_to_ocds.utils.date_utils import start_date

logger = logging.getLogger(__name__)


def parse_dispatch_invitation_tender(xml_content: str | bytes) -> dict | None:
    """Parse the dispatch invitation tender dates from lot-level XML data.

    Args:
        xml_content (Union[str, bytes]): The XML content containing lot information

    Returns:
        Optional[Dict]: Dictionary containing tender lot information, or None if no data found
        The structure follows the format:
        {
            "tender": {
                "lots": [
                    {
                        "id": str,
                        "secondStage": {
                            "invitationDate": str # ISO formatted date
                        }
                    }
                ]
            }
        }

    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")
    root = etree.fromstring(xml_content)
    namespaces = {
        "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
        "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
        "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
        "efext": "http://data.europa.eu/p27/eforms-ubl-extensions/1",
        "efbc": "http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1",
    }

    result = {"tender": {"lots": []}}

    lots = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']",
        namespaces=namespaces,
    )

    for lot in lots:
        lot_id = lot.xpath("cbc:ID[@schemeName='Lot']/text()", namespaces=namespaces)[0]
        invitation_date = lot.xpath(
            "cac:TenderingProcess/cac:InvitationSubmissionPeriod/cbc:StartDate/text()",
            namespaces=namespaces,
        )

        if invitation_date:
            try:
                iso_date = start_date(invitation_date[0])
                result["tender"]["lots"].append(
                    {
                        "id": lot_id,
                        "secondStage": {"invitationDate": iso_date},
                    }
                )
            except ValueError as e:
                logger.warning(
                    "Error parsing invitation date for lot %s: %s", lot_id, e
                )

    return result if result["tender"]["lots"] else None


def merge_dispatch_invitation_tender(
    release_json: dict, dispatch_invitation_data: dict | None
) -> None:
    """Merge dispatch invitation tender data into the release JSON.

    Args:
        release_json (Dict): The target release JSON to merge data into
        dispatch_invitation_data (Optional[Dict]): The source data containing tender lots
            to be merged. If None, function returns without making changes.

    Note:
        The function modifies release_json in-place by adding or updating the
        tender.lots.secondStage.invitationDate field for matching lots.

    """
    if not dispatch_invitation_data:
        logger.warning("No Dispatch Invitation Tender data to merge")
        return

    existing_lots = release_json.setdefault("tender", {}).setdefault("lots", [])

    for new_lot in dispatch_invitation_data["tender"]["lots"]:
        existing_lot = next(
            (lot for lot in existing_lots if lot["id"] == new_lot["id"]),
            None,
        )
        if existing_lot:
            existing_lot.setdefault("secondStage", {}).update(new_lot["secondStage"])
        else:
            existing_lots.append(new_lot)

    logger.info(
        "Merged Dispatch Invitation Tender data for %d lots",
        len(dispatch_invitation_data["tender"]["lots"]),
    )
