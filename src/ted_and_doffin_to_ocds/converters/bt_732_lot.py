import logging

from lxml import etree

logger = logging.getLogger(__name__)

NAMESPACES = {
    "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
    "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
    "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
    "efext": "http://data.europa.eu/p27/eforms-ubl-extensions/1",
    "efbc": "http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1",
}


def parse_lot_security_clearance_description(xml_content: str | bytes) -> dict | None:
    """Parse BT-732: Additional information about security clearance.

    Extracts information about required security clearances including level,
    team member requirements, and when clearance is needed.

    Args:
        xml_content: XML content to parse, either as string or bytes

    Returns:
        Optional[Dict]: Parsed data in format:
            {
                "tender": {
                    "lots": [
                        {
                            "id": str,
                            "otherRequirements": {
                                "securityClearance": str
                            }
                        }
                    ]
                }
            }
        Returns None if no relevant data found or on error

    """
    try:
        if isinstance(xml_content, str):
            xml_content = xml_content.encode("utf-8")
        root = etree.fromstring(xml_content)
        result = {"tender": {"lots": []}}

        lots = root.xpath(
            "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']",
            namespaces=NAMESPACES,
        )

        for lot in lots:
            lot_id = lot.xpath("cbc:ID/text()", namespaces=NAMESPACES)[0]
            security_clearance = lot.xpath(
                "cac:TenderingTerms/cac:SecurityClearanceTerm/cbc:Description/text()",
                namespaces=NAMESPACES,
            )

            if security_clearance:
                description = security_clearance[0].strip()
                logger.info(
                    "Found security clearance for lot %s: %s", lot_id, description
                )
                lot_data = {
                    "id": lot_id,
                    "otherRequirements": {"securityClearance": description},
                }
                result["tender"]["lots"].append(lot_data)

        return result if result["tender"]["lots"] else None

    except etree.XMLSyntaxError:
        logger.exception("Failed to parse XML content")
        raise
    except Exception:
        logger.exception("Error processing security clearance")
        return None


def merge_lot_security_clearance_description(
    release_json: dict, clearance_data: dict | None
) -> None:
    """Merge security clearance description data into the release JSON.

    Updates or adds security clearance requirements for lots.

    Args:
        release_json: Main OCDS release JSON to update
        clearance_data: Security clearance data to merge, can be None

    Note:
        - Updates release_json in-place
        - Creates tender.lots array if needed
        - Updates existing lots' otherRequirements

    """
    if not clearance_data:
        logger.warning("No lot security clearance description data to merge")
        return

    tender = release_json.setdefault("tender", {})
    tender.setdefault("lots", [])

    for new_lot in clearance_data["tender"]["lots"]:
        existing_lot = next(
            (lot for lot in tender["lots"] if lot["id"] == new_lot["id"]),
            None,
        )
        if existing_lot:
            existing_lot.setdefault("otherRequirements", {})
            existing_lot["otherRequirements"]["securityClearance"] = new_lot[
                "otherRequirements"
            ]["securityClearance"]
        else:
            tender["lots"].append(new_lot)

    logger.info(
        "Merged security clearance description data for %d lots",
        len(clearance_data["tender"]["lots"]),
    )
