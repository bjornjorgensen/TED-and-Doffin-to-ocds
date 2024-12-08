# converters/bt_109_lot.py

import logging

from lxml import etree

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
    """Validate and prepare XML content for processing.

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


def parse_framework_duration_justification(xml_content: str | bytes) -> dict | None:
    """Parse framework agreement duration justification from XML for each lot.

    Extract information about justification for exceptional cases when the duration
    of framework agreements exceeds the legal limits as defined in BT-109.

    Args:
        xml_content: The XML content to parse, either as a string or bytes.

    Returns:
        A dictionary containing the parsed data in OCDS format with the following structure:
        {
            "tender": {
                "lots": [
                    {
                        "id": str,
                        "techniques": {
                            "frameworkAgreement": {
                                "periodRationale": str
                            }
                        }
                    }
                ]
            }
        }
        Returns None if no relevant data is found.

    Raises:
        etree.XMLSyntaxError: If the input is not valid XML.

    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")

    root = etree.fromstring(xml_content)
    namespaces = {
        "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    }

    result = {"tender": {"lots": []}}

    lots = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']",
        namespaces=namespaces,
    )

    for lot in lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        justification = lot.xpath(
            ".//cac:TenderingProcess/cac:FrameworkAgreement/cbc:Justification/text()",
            namespaces=namespaces,
        )

        if justification and justification[0].strip():
            lot_data = {
                "id": lot_id,
                "techniques": {
                    "frameworkAgreement": {"periodRationale": justification[0].strip()}
                },
            }
            result["tender"]["lots"].append(lot_data)

    return result if result["tender"]["lots"] else None


def merge_framework_duration_justification(
    release_json: dict, framework_justification_data: dict | None
) -> None:
    """Merge framework duration justification data into the OCDS release.

    Updates the release JSON in-place by adding or updating framework agreement
    information for each lot specified in the input data.

    Args:
        release_json: The main OCDS release JSON to be updated. Must contain
            a 'tender' object with a 'lots' array.
        framework_justification_data: The parsed framework justification data
            in the same format as returned by parse_framework_duration_justification().
            If None, no changes will be made.

    Returns:
        None: The function modifies release_json in-place.

    """
    if not framework_justification_data:
        logger.info("No framework duration justification data to merge")
        return

    tender = release_json.setdefault("tender", {})
    existing_lots = tender.setdefault("lots", [])

    for new_lot in framework_justification_data["tender"]["lots"]:
        existing_lot = next(
            (lot for lot in existing_lots if lot["id"] == new_lot["id"]),
            None,
        )
        if existing_lot:
            techniques = existing_lot.setdefault("techniques", {})
            framework = techniques.setdefault("frameworkAgreement", {})
            framework["periodRationale"] = new_lot["techniques"]["frameworkAgreement"][
                "periodRationale"
            ]
        else:
            existing_lots.append(new_lot)

    logger.info(
        "Merged framework duration justification data for %d lots",
        len(framework_justification_data["tender"]["lots"]),
    )
