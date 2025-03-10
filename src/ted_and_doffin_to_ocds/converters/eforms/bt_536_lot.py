import logging
from typing import Any

from lxml import etree

from ted_and_doffin_to_ocds.utils.date_utils import start_date

logger = logging.getLogger(__name__)


def parse_lot_start_date(xml_content: str | bytes) -> dict[str, Any] | None:
    """Parse the start date (BT-536) for procurement project lots from XML content.

    Args:
        xml_content: XML string or bytes containing the procurement data

    Returns:
        Dict containing the parsed lot start date data in OCDS format, or None if no data found.
        Format:
        {
            "tender": {
                "lots": [
                    {
                        "id": "lot-id",
                        "contractPeriod": {
                            "startDate": "2019-11-15T00:00:00+01:00"
                        }
                    }
                ]
            }
        }

    """
    logger.info("Starting parse_lot_start_date function")
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
    logger.info("Found %d lots", len(lots))

    for lot in lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        date_to_start = lot.xpath(
            "cac:ProcurementProject/cac:PlannedPeriod/cbc:StartDate/text()",
            namespaces=namespaces,
        )

        logger.info("Processing lot %s", lot_id)

        if date_to_start:
            try:
                formatted_start_date = start_date(date_to_start[0])
                lot_data = {
                    "id": lot_id,
                    "contractPeriod": {"startDate": formatted_start_date},
                }
                result["tender"]["lots"].append(lot_data)
                logger.info("Added lot data: %s", lot_data)
            except ValueError:
                logger.exception("Error formatting start date for lot %s", lot_id)
        else:
            logger.warning("No start date found for lot %s", lot_id)

    return result if result["tender"]["lots"] else None


def merge_lot_start_date(
    release_json: dict[str, Any], lot_start_date_data: dict[str, Any] | None
) -> None:
    """Merge lot start date data into the main release JSON.

    Args:
        release_json: The main release JSON to merge data into
        lot_start_date_data: The lot start date data to merge from

    Returns:
        None - modifies release_json in place

    """
    if not lot_start_date_data:
        logger.warning("No lot start date data to merge")
        return

    tender = release_json.setdefault("tender", {})
    existing_lots = tender.setdefault("lots", [])

    for new_lot in lot_start_date_data["tender"]["lots"]:
        existing_lot = next(
            (lot for lot in existing_lots if lot["id"] == new_lot["id"]),
            None,
        )
        if existing_lot:
            existing_lot.setdefault("contractPeriod", {}).update(
                new_lot["contractPeriod"],
            )
            logger.info("Updated existing lot: %s", existing_lot)
        else:
            existing_lots.append(new_lot)
            logger.info("Added new lot: %s", new_lot)
