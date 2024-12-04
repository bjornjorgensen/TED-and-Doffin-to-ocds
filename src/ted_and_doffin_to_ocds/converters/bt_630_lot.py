# converters/bt_630_Lot.py

import logging
from typing import Any

from lxml import etree

from ted_and_doffin_to_ocds.utils.date_utils import end_date

logger = logging.getLogger(__name__)


def parse_deadline_receipt_expressions(
    xml_content: str | bytes,
) -> dict[str, Any] | None:
    """Parse the deadline for receipt of expressions (BT-630) for procurement project lots from XML content.

    Args:
        xml_content: XML string or bytes containing the procurement data

    Returns:
        Dict containing the parsed deadline data in OCDS format, or None if no data found.
        Format:
        {
            "tender": {
                "lots": [
                    {
                        "id": "LOT-0001",
                        "tenderPeriod": {
                            "endDate": "2019-10-28T18:00:00+01:00"
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
        end_date_xpath = ".//efac:InterestExpressionReceptionPeriod/cbc:EndDate/text()"
        end_time_xpath = ".//efac:InterestExpressionReceptionPeriod/cbc:EndTime/text()"

        end_date_value = lot.xpath(end_date_xpath, namespaces=namespaces)
        end_time_value = lot.xpath(end_time_xpath, namespaces=namespaces)

        if end_date_value:
            date_str = end_date_value[0]
            if end_time_value:
                # If we have both date and time, combine them
                time_str = end_time_value[0]
                # Extract date and time parts without timezone
                date_part = date_str.split("+")[0]
                time_part = time_str.split("+")[0]
                # Get timezone from date
                tz = f"+{date_str.split('+')[1]}" if "+" in date_str else "Z"
                iso_datetime = f"{date_part}T{time_part}{tz}"
            else:
                # If no time, use end_date helper which sets time to 23:59:59
                iso_datetime = end_date(date_str)

            lot_data = {"id": lot_id, "tenderPeriod": {"endDate": iso_datetime}}
            result["tender"]["lots"].append(lot_data)

    return result if result["tender"]["lots"] else None


def merge_deadline_receipt_expressions(
    release_json: dict[str, Any],
    deadline_receipt_expressions_data: dict[str, Any] | None,
) -> None:
    """Merge deadline receipt expressions data into the release JSON.

    Args:
        release_json: The main release JSON to merge data into
        deadline_receipt_expressions_data: The deadline receipt expressions data to merge from

    Returns:
        None - modifies release_json in place
    """
    if not deadline_receipt_expressions_data:
        logger.warning("No deadline receipt expressions data to merge")
        return

    tender = release_json.setdefault("tender", {})
    existing_lots = tender.setdefault("lots", [])

    for new_lot in deadline_receipt_expressions_data["tender"]["lots"]:
        existing_lot = next(
            (lot for lot in existing_lots if lot["id"] == new_lot["id"]),
            None,
        )
        if existing_lot:
            existing_lot.setdefault("tenderPeriod", {}).update(new_lot["tenderPeriod"])
        else:
            existing_lots.append(new_lot)

    logger.info(
        "Merged deadline receipt expressions data for %d lots",
        len(deadline_receipt_expressions_data["tender"]["lots"]),
    )
