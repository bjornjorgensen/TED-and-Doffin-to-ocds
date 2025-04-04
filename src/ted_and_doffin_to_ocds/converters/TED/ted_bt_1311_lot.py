import logging

from lxml import etree

from ted_and_doffin_to_ocds.utils.date_utils import convert_to_iso_format

logger = logging.getLogger(__name__)


def parse_deadline_receipt_requests(xml_content: str | bytes) -> dict | None:
    """Parse BT-1311: Time limit for receipt of requests to participate from TED format.

    Extracts date and time components for participation request deadline from TED XML.

    Args:
        xml_content: TED XML content to parse, either as string or bytes

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

        # Check different potential paths for defense contracts
        deadline_paths = [
            "//ADMINISTRATIVE_INFORMATION_CONTRACT_NOTICE_DEFENCE/RECEIPT_LIMIT_DATE",
            "//ADMINISTRATIVE_INFORMATION_CONTRACT_SUB_NOTICE_DEFENCE/RECEIPT_LIMIT_DATE",
            "//RECEIPT_LIMIT_DATE",  # Fallback for other formats
        ]

        for xpath in deadline_paths:
            deadline_nodes = root.xpath(xpath)
            if deadline_nodes:
                break

        if deadline_nodes:
            for node in deadline_nodes:
                try:
                    # Extract date components (YEAR, MONTH, DAY format in TED)
                    year = node.xpath("./YEAR/text()")
                    month = node.xpath("./MONTH/text()")
                    day = node.xpath("./DAY/text()")

                    # Extract time if available
                    time = node.xpath("./TIME/text()")

                    if year and month and day:
                        # Format date string
                        date_str = f"{year[0]}-{month[0].zfill(2)}-{day[0].zfill(2)}"
                        time_str = time[0] if time else "23:59:59"

                        # Combine to create ISO datetime
                        full_datetime = f"{date_str}T{time_str}Z"
                        iso_date = convert_to_iso_format(full_datetime)

                        # In TED format, lot information might not be explicitly defined
                        # For this implementation, we'll use default lot ID "1"
                        lot_id = "1"

                        logger.info(
                            "Processed TED deadline: %s (date: %s, time: %s)",
                            iso_date,
                            date_str,
                            time_str if time else "end of day",
                        )

                        result["tender"]["lots"].append(
                            {"id": lot_id, "tenderPeriod": {"endDate": iso_date}}
                        )
                except (ValueError, IndexError) as e:
                    logger.warning("Error parsing TED deadline: %s", str(e))

        return result if result["tender"]["lots"] else None

    except etree.XMLSyntaxError:
        logger.exception("Failed to parse TED XML content")
        raise
    except Exception:
        logger.exception("Error processing TED participation request deadlines")
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
        logger.warning("No TED deadline receipt requests data to merge")
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
        "Merged TED deadline receipt requests data for %d lots",
        len(deadline_data["tender"]["lots"]),
    )
