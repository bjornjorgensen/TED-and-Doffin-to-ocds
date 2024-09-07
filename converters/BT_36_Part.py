# converters/BT_36_Part.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)


def parse_part_duration(xml_content):
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

    duration_measure = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']/cac:ProcurementProject/cac:PlannedPeriod/cbc:DurationMeasure",
        namespaces=namespaces,
    )

    if duration_measure:
        duration_value = int(duration_measure[0].text)
        unit_code = duration_measure[0].get("unitCode")

        if unit_code == "DAY":
            duration_in_days = duration_value
        elif unit_code == "MONTH":
            duration_in_days = duration_value * 30
        elif unit_code == "YEAR":
            duration_in_days = duration_value * 365
        elif unit_code in ["WEEK", "MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]:
            duration_in_days = duration_value * 7
        else:
            logger.warning(f"Unknown unitCode '{unit_code}' for part duration")
            return None

        result["tender"]["contractPeriod"] = {"durationInDays": duration_in_days}

    return result if "contractPeriod" in result["tender"] else None


def merge_part_duration(release_json, part_duration_data):
    if not part_duration_data:
        logger.warning("No part duration data to merge")
        return

    release_json.setdefault("tender", {}).setdefault("contractPeriod", {}).update(
        part_duration_data["tender"]["contractPeriod"]
    )

    logger.info("Merged part duration data")
