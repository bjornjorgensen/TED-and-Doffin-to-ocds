# converters/bt_36_part.py

import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)

NAMESPACES = {
    "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
    "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
    "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
    "efext": "http://data.europa.eu/p27/eforms-ubl-extensions/1",
    "efbc": "http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1",
}


def parse_part_duration(xml_content: str | bytes) -> dict[str, Any] | None:
    """Parse the contract duration from XML content.

    Args:
        xml_content: XML string or bytes to parse

    Returns:
        Dictionary containing tender contract period duration or None if not found

    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")

    root = etree.fromstring(xml_content)
    duration_measures = root.xpath(
        "/*/cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']/cac:ProcurementProject/cac:PlannedPeriod/cbc:DurationMeasure",
        namespaces=NAMESPACES,
    )

    if not duration_measures:
        logger.debug("No duration measure found in XML")
        return None

    try:
        duration_value = int(duration_measures[0].text.strip())
        unit_code = duration_measures[0].get("unitCode")

        if not unit_code:
            logger.warning("Missing unitCode for duration measure")
            return None

        duration_in_days = calculate_duration_in_days(duration_value, unit_code)
        if duration_in_days is None:
            return None

        logger.debug(
            "Parsed duration: %s %s -> %s days",
            duration_value,
            unit_code,
            duration_in_days,
        )
    except (ValueError, TypeError):
        logger.exception("Invalid duration value")
        return None
    else:
        return {"tender": {"contractPeriod": {"durationInDays": duration_in_days}}}


def calculate_duration_in_days(value: int, unit_code: str) -> int | None:
    """Calculate duration in days based on unit code.

    Args:
        value: Duration value
        unit_code: Unit code from XML (DAY, MONTH, YEAR)

    Returns:
        Duration in days or None if unit code is invalid

    """
    unit_code = unit_code.upper()

    # Map duration units to number of days
    duration_mappings = {
        "DAY": 1,
        "MONTH": 30,
        "YEAR": 365,
    }

    multiplier = duration_mappings.get(unit_code)
    if multiplier is None:
        logger.warning("Unknown unitCode '%s' for duration", unit_code)
        return None

    return value * multiplier


def merge_part_duration(
    release_json: dict[str, Any], part_duration_data: dict[str, Any] | None
) -> None:
    """Merge duration data into the release JSON.

    Args:
        release_json: The target release JSON to update
        part_duration_data: The duration data to merge

    """
    if not part_duration_data:
        logger.debug("No duration data to merge")
        return

    tender = release_json.setdefault("tender", {})
    contract_period = tender.setdefault("contractPeriod", {})
    contract_period["durationInDays"] = part_duration_data["tender"]["contractPeriod"][
        "durationInDays"
    ]

    logger.info("Merged contract duration: %d days", contract_period["durationInDays"])
