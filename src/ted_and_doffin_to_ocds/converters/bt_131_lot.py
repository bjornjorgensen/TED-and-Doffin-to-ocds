# converters/bt_131_Lot.py

import logging

from lxml import etree

from ted_and_doffin_to_ocds.utils.date_utils import end_date

logger = logging.getLogger(__name__)


def parse_deadline_receipt_tenders(xml_content: str | bytes) -> dict | None:
    """
    Parse the tender submission deadline from lot-level XML data.

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
                        "tenderPeriod": {
                            "endDate": str # ISO formatted date
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
        end_date_str = lot.xpath(
            "cac:TenderingProcess/cac:TenderSubmissionDeadlinePeriod/cbc:EndDate/text()",
            namespaces=namespaces,
        )
        end_time_str = lot.xpath(
            "cac:TenderingProcess/cac:TenderSubmissionDeadlinePeriod/cbc:EndTime/text()",
            namespaces=namespaces,
        )

        if end_date_str:
            try:
                # Combine date and time if available, otherwise just use date
                date_str = end_date_str[0]
                if end_time_str:
                    date_str = f"{date_str.split('+')[0]}T{end_time_str[0]}"
                deadline = end_date(date_str)
                result["tender"]["lots"].append(
                    {"id": lot_id, "tenderPeriod": {"endDate": deadline}}
                )
            except ValueError as e:
                logger.warning("Error parsing deadline for lot %s: %s", lot_id, e)

    return result if result["tender"]["lots"] else None


def merge_deadline_receipt_tenders(
    release_json: dict, deadline_data: dict | None
) -> None:
    """
    Merge tender submission deadline data into the release JSON.

    Args:
        release_json (Dict): The target release JSON to merge data into
        deadline_data (Optional[Dict]): The source data containing tender lots
            to be merged. If None, function returns without making changes.

    Note:
        The function modifies release_json in-place by adding or updating the
        tender.lots.tenderPeriod.endDate field for matching lots.
    """
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
