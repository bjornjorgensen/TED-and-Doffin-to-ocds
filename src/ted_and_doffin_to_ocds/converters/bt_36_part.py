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
    """
    Parse the contract duration from XML content.

    Args:
        xml_content: XML string or bytes to parse

    Returns:
        Dictionary containing tender contract period duration or None if not found

    Raises:
        etree.XMLSyntaxError: If XML content is invalid
    """
    try:
        if isinstance(xml_content, str):
            xml_content = xml_content.encode("utf-8")

        root = etree.fromstring(xml_content)

        # Target the correct XPath for BT-36
        duration_measures = root.xpath(
            "/*/cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']/cac:ProcurementProject/cac:PlannedPeriod/cbc:DurationMeasure",
            namespaces=NAMESPACES,
        )

        if not duration_measures:
            logger.debug("No duration measure found")
            return None

        duration_measure = duration_measures[0]
        duration_value = int(duration_measure.text)
        unit_code = duration_measure.get("unitCode")

        if not unit_code:
            logger.warning("No unitCode found for duration measure")
            return None

        # Convert duration based on unit code
        duration_in_days = calculate_duration_in_days(duration_value, unit_code)
        if duration_in_days is None:
            return None

        logger.info(
            "Found duration: %d %s (converted to %d days)",
            duration_value,
            unit_code,
            duration_in_days,
        )

        return {"tender": {"contractPeriod": {"durationInDays": duration_in_days}}}  # noqa: TRY300

    except etree.XMLSyntaxError:
        logger.exception("Failed to parse XML content")
        raise
    except ValueError:
        logger.exception("Invalid duration value")
        return None


def calculate_duration_in_days(value: int, unit_code: str) -> int | None:
    """
    Calculate duration in days based on unit code.

    Args:
        value: Duration value
        unit_code: Unit code from XML

    Returns:
        Duration in days or None if unit code is invalid
    """
    unit_code = unit_code.upper()

    if unit_code == "DAY":
        return value
    if unit_code == "MONTH":
        return value * 30
    if unit_code == "YEAR":
        return value * 365
    if unit_code in ["WEEK", "MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]:
        return value * 7

    logger.warning("Unknown unitCode '%s' for duration", unit_code)
    return None


def merge_part_duration(
    release_json: dict[str, Any], part_duration_data: dict[str, Any] | None
) -> None:
    """
    Merge duration data into the release JSON.

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
