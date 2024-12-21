# converters/bt_537_part.py

import logging
from typing import Any

from lxml import etree

from ted_and_doffin_to_ocds.utils.date_utils import end_date

logger = logging.getLogger(__name__)


def parse_part_duration_end_date(
    xml_content: str | bytes,
) -> dict[str, Any] | None:
    """Parse the end date (BT-537) for procurement project parts from XML content.

    This function extracts the end date from ProcurementProjectLot elements with schemeName='Part'
    and converts it to ISO format with time set to 23:59:59.

    Args:
        xml_content: XML string or bytes containing the procurement data

    Returns:
        Dict containing the parsed part end date data in OCDS format, or None if no data found.
        Format:
        {
            "tender": {
                "contractPeriod": {
                    "endDate": "2019-11-19T23:59:59+01:00"
                }
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

    result = {"tender": {}}

    xpath_query = "/*/cac:ProcurementProjectLot[cbc:ID/@schemeName='part']/cac:ProcurementProject/cac:PlannedPeriod/cbc:EndDate"
    end_date_elements = root.xpath(xpath_query, namespaces=namespaces)

    if end_date_elements:
        try:
            date_to_end = end_date_elements[0].text
            iso_end_date = end_date(date_to_end)
            result["tender"]["contractPeriod"] = {"endDate": iso_end_date}
        except ValueError as e:
            logging.warning("Warning: Invalid date format for part end date: %s", e)

    return result if "contractPeriod" in result["tender"] else None


def merge_part_duration_end_date(
    release_json: dict[str, Any], part_duration_end_date_data: dict[str, Any] | None
) -> None:
    """Merge part duration end date data into the main release JSON.

    Args:
        release_json: The main release JSON to merge data into
        part_duration_end_date_data: The part duration end date data to merge from

    Returns:
        None - modifies release_json in place

    """
    if not part_duration_end_date_data:
        return

    release_json.setdefault("tender", {}).setdefault("contractPeriod", {}).update(
        part_duration_end_date_data["tender"]["contractPeriod"],
    )
