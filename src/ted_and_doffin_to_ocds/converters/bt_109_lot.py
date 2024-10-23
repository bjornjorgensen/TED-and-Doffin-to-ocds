# converters/bt_109_lot.py

import logging
from lxml import etree
from typing import Any

logger = logging.getLogger(__name__)

# Constants
XPATH_FRAMEWORK_JUSTIFICATION = "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']/cac:TenderingProcess/cac:FrameworkAgreement/cbc:Justification"
NAMESPACES = {
    "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
    "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
}

# Error messages
ERR_EMPTY_XML = "XML content cannot be None or empty"
ERR_INVALID_RELEASE_JSON = "release_json must be a dictionary"


def validate_xml_content(xml_content: str | bytes) -> bytes:
    """
    Validate and prepare XML content for processing.

    Args:
        xml_content: The XML content to validate.

    Returns:
        bytes: The validated XML content.

    Raises:
        ValueError: If the input is None or empty.
        etree.XMLSyntaxError: If the XML is malformed.
    """
    if not xml_content:
        raise ValueError(ERR_EMPTY_XML)

    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")

    try:
        etree.fromstring(xml_content)
    except etree.XMLSyntaxError:
        logger.exception("Invalid XML content")
        raise

    return xml_content


def parse_framework_duration_justification(
    xml_content: str | bytes,
) -> dict[str, Any] | None:
    """
    Parse the XML content to extract the framework agreement duration justification.

    Args:
        xml_content: The XML content to parse.

    Returns:
        Optional[Dict[str, Any]]: A dictionary containing the parsed framework
        duration justification data, or None if no relevant data is found.

    Raises:
        ValueError: If the input is invalid.
        etree.XMLSyntaxError: If the XML is malformed.
    """
    try:
        xml_content = validate_xml_content(xml_content)
        root = etree.fromstring(xml_content)

        result = {"tender": {"lots": []}}

        # Find all procurement project lots with framework justifications
        lots = root.xpath(
            "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']",
            namespaces=NAMESPACES,
        )

        for lot in lots:
            # Get lot ID
            lot_id = lot.xpath("cbc:ID/text()", namespaces=NAMESPACES)
            if not lot_id:
                continue

            # Get framework justification
            justification = lot.xpath(
                ".//cac:TenderingProcess/cac:FrameworkAgreement/cbc:Justification/text()",
                namespaces=NAMESPACES,
            )
            if not justification or not justification[0].strip():
                continue

            lot_data = {
                "id": lot_id[0],
                "techniques": {
                    "frameworkAgreement": {"periodRationale": justification[0].strip()}
                },
            }
            result["tender"]["lots"].append(lot_data)

        return result if result["tender"]["lots"] else None

    except (ValueError, etree.XMLSyntaxError):
        logger.exception("Error parsing framework duration justification")
        raise
    except Exception:
        logger.exception("Unexpected error parsing framework duration justification")
        raise


def merge_framework_duration_justification(
    release_json: dict[str, Any], framework_justification_data: dict[str, Any] | None
) -> None:
    """
    Merge the parsed framework duration justification data into the main OCDS release JSON.

    Args:
        release_json: The main OCDS release JSON to be updated.
        framework_justification_data: The parsed framework justification data to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not isinstance(release_json, dict):
        logger.error("Invalid release_json type: %s", type(release_json))
        raise TypeError(ERR_INVALID_RELEASE_JSON)

    if not framework_justification_data:
        logger.info("No framework duration justification data to merge")
        return

    tender = release_json.setdefault("tender", {})
    existing_lots = tender.setdefault("lots", [])

    try:
        for new_lot in framework_justification_data["tender"]["lots"]:
            if (
                not new_lot.get("techniques", {})
                .get("frameworkAgreement", {})
                .get("periodRationale")
            ):
                continue

            existing_lot = next(
                (lot for lot in existing_lots if lot["id"] == new_lot["id"]), None
            )

            if existing_lot:
                techniques = existing_lot.setdefault("techniques", {})
                framework = techniques.setdefault("frameworkAgreement", {})
                framework["periodRationale"] = new_lot["techniques"][
                    "frameworkAgreement"
                ]["periodRationale"]
            else:
                existing_lots.append(new_lot)

            logger.debug(
                "Updated framework duration justification for lot %s", new_lot["id"]
            )

        logger.info(
            "Successfully merged framework duration justification data for %d lots",
            len(framework_justification_data["tender"]["lots"]),
        )

    except KeyError:
        logger.warning("Missing required keys in framework_justification_data")
