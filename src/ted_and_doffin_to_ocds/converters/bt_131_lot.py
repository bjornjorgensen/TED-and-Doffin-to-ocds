# converters/bt_131_Lot.py

import logging
from lxml import etree
from datetime import datetime, timezone, timedelta, UTC

logger = logging.getLogger(__name__)


def parse_deadline_receipt_tenders(xml_content):
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
    logger.info("Found %s lots in XML", len(lots))

    for lot in lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)
        if not lot_id:
            logger.warning("Lot ID not found, skipping this lot")
            continue
        lot_id = lot_id[0]

        end_date = lot.xpath(
            "cac:TenderingProcess/cac:TenderSubmissionDeadlinePeriod/cbc:EndDate/text()",
            namespaces=namespaces,
        )
        end_time = lot.xpath(
            "cac:TenderingProcess/cac:TenderSubmissionDeadlinePeriod/cbc:EndTime/text()",
            namespaces=namespaces,
        )

        logger.info(
            "Processing lot %s: EndDate=%s, EndTime=%s", lot_id, end_date, end_time
        )

        if end_date:
            try:
                date_str = end_date[0]
                time_str = end_time[0] if end_time else "23:59:59"

                # Combine date and time
                datetime_str = f"{date_str.split('+')[0]}T{time_str}"

                # Parse the datetime string
                dt = datetime.fromisoformat(datetime_str)

                # Add timezone information if present in the original string
                if "+" in date_str:
                    tz_offset = date_str.split("+")[1]
                    dt = dt.replace(
                        tzinfo=timezone(
                            timedelta(
                                hours=int(tz_offset.split(":")[0]),
                                minutes=int(tz_offset.split(":")[1]),
                            ),
                        ),
                    )
                else:
                    dt = dt.replace(tzinfo=UTC)

                iso_date = dt.isoformat()

                result["tender"]["lots"].append(
                    {"id": lot_id, "tenderPeriod": {"endDate": iso_date}},
                )
                logger.info(
                    "Successfully processed lot %s with endDate: %s",
                    lot_id,
                    iso_date,
                )
            except ValueError:
                logger.exception("Error parsing deadline for lot %s", lot_id)
        else:
            logger.warning("No EndDate found for lot %s, skipping this lot", lot_id)

    logger.info("Processed %s lots in total", len(result["tender"]["lots"]))
    return result if result["tender"]["lots"] else None


def merge_deadline_receipt_tenders(release_json, deadline_data):
    if not deadline_data:
        logger.warning("No Deadline Receipt Tenders data to merge")
        return

    existing_lots = release_json.setdefault("tender", {}).setdefault("lots", [])

    for new_lot in deadline_data["tender"]["lots"]:
        existing_lot = next(
            (lot for lot in existing_lots if lot["id"] == new_lot["id"]),
            None,
        )
        if existing_lot:
            existing_lot.setdefault("tenderPeriod", {}).update(new_lot["tenderPeriod"])
            logger.info("Updated existing lot %s with tenderPeriod data", new_lot["id"])
        else:
            existing_lots.append(new_lot)
            logger.info("Added new lot %s with tenderPeriod data", new_lot["id"])

    logger.info(
        "Merged Deadline Receipt Tenders data for %d lots",
        len(deadline_data["tender"]["lots"]),
    )
