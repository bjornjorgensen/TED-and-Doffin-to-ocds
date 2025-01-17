# converters/bt_19_Lot.py

import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)

JUSTIFICATION_CODES = {
    "ipr-iss": "Intellectual property right issues",
    "phy-mod": "Inclusion of a physical model",
    "sen-info": "Protection of particularly sensitive information",
    "sp-of-eq": "buyer would need specialised office equipment",
    "tdf-non-av": "Tools, devices, or file formats not generally available",
}


def parse_submission_nonelectronic_justification(
    xml_content: str,
) -> dict[str, Any] | None:
    """Parse non-electronic submission justification for each lot from XML content.

    Args:
        xml_content (str): The XML content to parse

    Returns:
        Optional[Dict[str, Any]]: Dictionary containing lots data with submission justifications,
                                 or None if no valid data is found

    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")

    try:
        root = etree.fromstring(xml_content)
    except etree.XMLSyntaxError:
        logger.exception("Failed to parse XML content")
        return None

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
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)
        if not lot_id:
            logger.warning("Lot ID not found")
            continue

        lot_id = lot_id[0]
        justification_code = lot.xpath(
            "cac:TenderingProcess/cac:ProcessJustification[cbc:ProcessReasonCode/@listName='no-esubmission-justification']/cbc:ProcessReasonCode/text()",
            namespaces=namespaces,
        )

        if justification_code:
            justification = JUSTIFICATION_CODES.get(justification_code[0])
            if justification:
                result["tender"]["lots"].append(
                    {
                        "id": lot_id,
                        "submissionTerms": {
                            "nonElectronicSubmission": {"rationale": justification},
                        },
                    },
                )

    return result if result["tender"]["lots"] else None


def merge_submission_nonelectronic_justification(
    release_json: dict[str, Any], justification_data: dict[str, Any] | None
) -> None:
    """Merge non-electronic submission justification data into the release JSON.

    Args:
        release_json (Dict[str, Any]): The release JSON to update
        justification_data (Optional[Dict[str, Any]]): Lot data containing submission justifications to merge

    """
    if not justification_data:
        logger.warning("No Submission Nonelectronic Justification data to merge")
        return

    existing_lots = release_json.setdefault("tender", {}).setdefault("lots", [])

    for new_lot in justification_data["tender"]["lots"]:
        existing_lot = next(
            (lot for lot in existing_lots if lot["id"] == new_lot["id"]),
            None,
        )
        if existing_lot:
            existing_lot.setdefault("submissionTerms", {}).setdefault(
                "nonElectronicSubmission",
                {},
            ).update(new_lot["submissionTerms"]["nonElectronicSubmission"])
        else:
            existing_lots.append(new_lot)

    logger.info(
        "Merged Submission Nonelectronic Justification data for %d lots",
        len(justification_data["tender"]["lots"]),
    )
