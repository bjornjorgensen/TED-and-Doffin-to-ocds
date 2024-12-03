# converters/bt_78_Lot.py

import logging

from lxml import etree

from ted_and_doffin_to_ocds.utils.date_utils import end_date

logger = logging.getLogger(__name__)


def parse_security_clearance_deadline(xml_content: str | bytes) -> dict | None:
    """Parse security clearance deadline from XML for each lot.

    Extract information about the time limit by which tenderers who do not hold
    a security clearance may obtain it as defined in BT-78.

    Args:
        xml_content: The XML content to parse, either as a string or bytes.

    Returns:
        A dictionary containing the parsed data in OCDS format with the following structure:
        {
            "tender": {
                "lots": [
                    {
                        "id": str,
                        "milestones": [
                            {
                                "id": "1",
                                "type": "securityClearanceDeadline",
                                "dueDate": str  # ISO formatted date
                            }
                        ]
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
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        security_clearance_date = lot.xpath(
            "cac:TenderingTerms/cbc:LatestSecurityClearanceDate/text()",
            namespaces=namespaces,
        )

        if security_clearance_date:
            lot_data = {
                "id": lot_id,
                "milestones": [
                    {
                        "id": "1",
                        "type": "securityClearanceDeadline",
                        "dueDate": end_date(security_clearance_date[0]),
                    },
                ],
            }
            result["tender"]["lots"].append(lot_data)

    return result if result["tender"]["lots"] else None


def merge_security_clearance_deadline(
    release_json: dict, security_clearance_data: dict | None
) -> None:
    """Merge security clearance deadline data into the OCDS release.

    Updates the release JSON in-place by adding or updating milestones
    for each lot specified in the input data.

    Args:
        release_json: The main OCDS release JSON to be updated. Must contain
            a 'tender' object with a 'lots' array.
        security_clearance_data: The parsed security clearance data
            in the same format as returned by parse_security_clearance_deadline().
            If None, no changes will be made.

    Returns:
        None: The function modifies release_json in-place.
    """
    if not security_clearance_data:
        logger.warning("No Security Clearance Deadline data to merge")
        return

    tender = release_json.setdefault("tender", {})
    existing_lots = tender.setdefault("lots", [])

    for new_lot in security_clearance_data["tender"]["lots"]:
        existing_lot = next(
            (lot for lot in existing_lots if lot["id"] == new_lot["id"]),
            None,
        )
        if existing_lot:
            existing_milestones = existing_lot.setdefault("milestones", [])
            existing_milestones.extend(new_lot["milestones"])
        else:
            existing_lots.append(new_lot)

    logger.info(
        "Merged Security Clearance Deadline data for %d lots",
        len(security_clearance_data["tender"]["lots"]),
    )
