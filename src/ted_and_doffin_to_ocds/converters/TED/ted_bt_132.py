import logging

from lxml import etree

from ted_and_doffin_to_ocds.utils.date_utils import convert_to_iso_format

logger = logging.getLogger(__name__)


def parse_lot_public_opening_date(xml_content: str | bytes) -> dict | None:
    """Parse the public opening date from TED XML data.

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
                        "awardPeriod": {
                            "startDate": str # ISO formatted date with time
                        },
                        "bidOpening": {
                            "date": str # Same as awardPeriod.startDate
                        }
                    }
                ]
            }
        }
    """
    try:
        if isinstance(xml_content, str):
            xml_content = xml_content.encode("utf-8")
        root = etree.fromstring(xml_content)
        result = {"tender": {"lots": []}}

        # Try F02_2014 and F05_2014 forms
        form_types = ["F02_2014", "F05_2014"]

        for form_type in form_types:
            # Extract date and time
            date_path = f"//TED_EXPORT/FORM_SECTION/{form_type}/PROCEDURE/OPENING_CONDITION/DATE_OPENING_TENDERS/text()"
            time_path = f"//TED_EXPORT/FORM_SECTION/{form_type}/PROCEDURE/OPENING_CONDITION/TIME_OPENING_TENDERS/text()"

            date_nodes = root.xpath(date_path)
            time_nodes = root.xpath(time_path)

            if date_nodes:
                date_str = date_nodes[0]
                time_str = time_nodes[0] if time_nodes else "00:00:00"

                try:
                    # Combine date and time
                    full_datetime = f"{date_str}T{time_str}"
                    iso_date = convert_to_iso_format(full_datetime)

                    # In TED, we don't have lot-specific public opening dates,
                    # so we apply the same date to all lots or create a dummy lot
                    lot_ids = root.xpath(
                        f"//TED_EXPORT/FORM_SECTION/{form_type}/OBJECT_CONTRACT/LOT_DIVISION/LOT_INFO/LOT_NO/text()"
                    )

                    if lot_ids:
                        for lot_id in lot_ids:
                            lot_data = {
                                "id": lot_id,
                                "awardPeriod": {"startDate": iso_date},
                                "bidOpening": {"date": iso_date},
                            }
                            result["tender"]["lots"].append(lot_data)
                    else:
                        # If no lots specified, create a single lot entry
                        lot_data = {
                            "id": "1",  # Default lot ID
                            "awardPeriod": {"startDate": iso_date},
                            "bidOpening": {"date": iso_date},
                        }
                        result["tender"]["lots"].append(lot_data)

                    logger.info(
                        "Processed public opening date: %s (date: %s, time: %s)",
                        iso_date,
                        date_str,
                        time_str,
                    )

                except (ValueError, IndexError) as e:
                    logger.warning("Error parsing public opening date: %s", str(e))

                # We found data in this form type, no need to check others
                break

        return result if result["tender"]["lots"] else None

    except etree.XMLSyntaxError:
        logger.exception("Failed to parse XML content")
        raise
    except Exception:
        logger.exception("Error processing public opening date")
        return None


def merge_lot_public_opening_date(
    release_json: dict, lot_public_opening_date_data: dict | None
) -> None:
    """Merge public opening date data into the release JSON.

    Args:
        release_json (Dict): The target release JSON to merge data into
        lot_public_opening_date_data (Optional[Dict]): The source data containing tender lots
            to be merged. If None, function returns without making changes.

    Note:
        The function modifies release_json in-place by adding or updating the
        tender.lots.awardPeriod.startDate and tender.lots.bidOpening.date fields.
    """
    if not lot_public_opening_date_data:
        logger.warning("No public opening date data to merge")
        return

    tender = release_json.setdefault("tender", {})
    lots = tender.setdefault("lots", [])

    for new_lot in lot_public_opening_date_data["tender"]["lots"]:
        existing_lot = next((lot for lot in lots if lot["id"] == new_lot["id"]), None)
        if existing_lot:
            existing_lot.setdefault("awardPeriod", {})["startDate"] = new_lot[
                "awardPeriod"
            ]["startDate"]
            existing_lot["bidOpening"] = new_lot["bidOpening"]
            logger.info(
                "Updated public opening date for lot %s: %s",
                new_lot["id"],
                new_lot["awardPeriod"]["startDate"],
            )
        else:
            lots.append(new_lot)
            logger.info("Added new lot %s with public opening date", new_lot["id"])

    logger.info(
        "Merged public opening date data for %d lots",
        len(lot_public_opening_date_data["tender"]["lots"]),
    )
