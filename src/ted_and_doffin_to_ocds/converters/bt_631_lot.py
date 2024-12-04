# converters/bt_631_Lot.py

import logging
from typing import Any

from lxml import etree

from ted_and_doffin_to_ocds.utils.date_utils import start_date

logger = logging.getLogger(__name__)


def parse_dispatch_invitation_interest(
    xml_content: str | bytes,
) -> dict[str, Any] | None:
    """Parse the dispatch invitation interest date (BT-631) for procurement project lots from XML content.

    Args:
        xml_content: XML string or bytes containing the procurement data

    Returns:
        Dict containing the parsed dispatch invitation interest date in OCDS format, or None if no data found.
        Format:
        {
            "tender": {
                "lots": [
                    {
                        "id": "LOT-0001",
                        "communication": {
                            "invitationToConfirmInterestDispatchDate": "2019-11-15T09:00:00+01:00"
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
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        dispatch_date = lot.xpath(
            "cac:TenderingProcess/cac:ParticipationInvitationPeriod/cbc:StartDate/text()",
            namespaces=namespaces,
        )

        if dispatch_date:
            iso_date = start_date(dispatch_date[0])
            lot_data = {
                "id": lot_id,
                "communication": {"invitationToConfirmInterestDispatchDate": iso_date},
            }
            result["tender"]["lots"].append(lot_data)

    return result if result["tender"]["lots"] else None


def merge_dispatch_invitation_interest(
    release_json: dict[str, Any],
    dispatch_invitation_data: dict[str, Any] | None,
) -> None:
    """Merge dispatch invitation interest data into the release JSON.

    Args:
        release_json: The main release JSON to merge data into
        dispatch_invitation_data: The dispatch invitation interest data to merge from

    Returns:
        None - modifies release_json in place
    """
    if not dispatch_invitation_data:
        logger.warning("No dispatch invitation interest data to merge")
        return

    existing_lots = release_json.setdefault("tender", {}).setdefault("lots", [])

    for new_lot in dispatch_invitation_data["tender"]["lots"]:
        existing_lot = next(
            (lot for lot in existing_lots if lot["id"] == new_lot["id"]),
            None,
        )
        if existing_lot:
            existing_lot.setdefault("communication", {}).update(
                new_lot["communication"],
            )
        else:
            existing_lots.append(new_lot)

    logger.info(
        "Merged dispatch invitation interest data for %d lots",
        len(dispatch_invitation_data["tender"]["lots"]),
    )
