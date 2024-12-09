# converters/bt_1311_Lot.py

import logging

from lxml import etree

from ted_and_doffin_to_ocds.utils.date_utils import convert_to_iso_format

logger = logging.getLogger(__name__)

NAMESPACES = {
    "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
    "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
}


def parse_deadline_receipt_requests(xml_content: str | bytes) -> dict | None:
    """Parse BT-1311: Time limit for receipt of requests to participate.

    Combines date and time components for participation request deadline.

    Args:
        xml_content: XML content to parse, either as string or bytes

    Returns:
        Optional[Dict]: Parsed data in format:
            {
                "tender": {
                    "lots": [
                        {
                            "id": str,
                            "tenderPeriod": {
                                "endDate": str  # ISO format datetime
                            }
                        }
                    ]
                }
            }
        Returns None if no relevant data found or on error

    """
    try:
        if isinstance(xml_content, str):
            xml_content = xml_content.encode("utf-8")
        root = etree.fromstring(xml_content)
        result = {"tender": {"lots": []}}

        lots = root.xpath(
            "/*/cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']",
            namespaces=NAMESPACES,
        )

        for lot in lots:
            lot_id = lot.xpath("cbc:ID/text()", namespaces=NAMESPACES)
            if not lot_id:
                continue

            end_date = lot.xpath(
                "cac:TenderingProcess/cac:ParticipationRequestReceptionPeriod/cbc:EndDate/text()",
                namespaces=NAMESPACES,
            )
            end_time = lot.xpath(
                "cac:TenderingProcess/cac:ParticipationRequestReceptionPeriod/cbc:EndTime/text()",
                namespaces=NAMESPACES,
            )

            if end_date:
                try:
                    # Combine date with time if available, otherwise use end of day
                    date_str = end_date[0]
                    time_str = end_time[0] if end_time else "23:59:59"

                    # Split timezone if present
                    base_date = date_str.split("+")[0]
                    tz = f"+{date_str.split('+')[1]}" if "+" in date_str else "Z"

                    # Combine all parts
                    full_datetime = f"{base_date}T{time_str}{tz}"
                    iso_date = convert_to_iso_format(full_datetime)

                    logger.info(
                        "Processed deadline for lot %s: %s", lot_id[0], iso_date
                    )
                    result["tender"]["lots"].append(
                        {"id": lot_id[0], "tenderPeriod": {"endDate": iso_date}}
                    )
                except (ValueError, IndexError) as e:
                    logger.warning(
                        "Error parsing deadline for lot %s: %s", lot_id[0], str(e)
                    )

        return result if result["tender"]["lots"] else None

    except etree.XMLSyntaxError:
        logger.exception("Failed to parse XML content")
        raise
    except Exception:
        logger.exception("Error processing participation request deadlines")
        return None


def merge_deadline_receipt_requests(
    release_json: dict, deadline_data: dict | None
) -> None:
    """Merge participation request deadline data into the release JSON.

    Updates or adds tender period end dates to lots.

    Args:
        release_json: Main OCDS release JSON to update
        deadline_data: Deadline data to merge, can be None

    Note:
        - Updates release_json in-place
        - Creates tender.lots array if needed
        - Updates existing lots' tenderPeriod

    """
    if not deadline_data:
        logger.warning("No deadline receipt requests data to merge")
        return

    tender = release_json.setdefault("tender", {})
    lots = tender.setdefault("lots", [])

    for new_lot in deadline_data["tender"]["lots"]:
        existing_lot = next((lot for lot in lots if lot["id"] == new_lot["id"]), None)
        if existing_lot:
            tender_period = existing_lot.setdefault("tenderPeriod", {})
            tender_period["endDate"] = new_lot["tenderPeriod"]["endDate"]
            logger.info(
                "Updated tender period for lot %s: %s",
                new_lot["id"],
                tender_period["endDate"],
            )
        else:
            lots.append(new_lot)
            logger.info("Added new lot %s with tender period", new_lot["id"])

    logger.info(
        "Merged deadline receipt requests data for %d lots",
        len(deadline_data["tender"]["lots"]),
    )
