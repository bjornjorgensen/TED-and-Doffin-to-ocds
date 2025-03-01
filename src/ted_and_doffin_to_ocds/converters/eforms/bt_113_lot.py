import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_framework_max_participants(xml_content: str | bytes) -> dict | None:
    """Parse framework agreement maximum participants from XML for each lot.

    Extract information about the maximum number of participants in the framework
    agreement as defined in BT-113.

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
                                "maximumParticipants": int
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
        "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
        "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
        "efext": "http://data.europa.eu/p27/eforms-ubl-extensions/1",
        "efbc": "http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1",
        "ted": "http://publications.europa.eu/resource/schema/ted/R2.0.9/publication",
    }

    result = {"tender": {"lots": []}}

    # Try eForms format first
    lots = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']",
        namespaces=namespaces,
    )

    if lots:
        for lot in lots:
            lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
            max_participants = lot.xpath(
                "cac:TenderingProcess/cac:FrameworkAgreement/cbc:MaximumOperatorQuantity/text()",
                namespaces=namespaces,
            )

            if max_participants:
                try:
                    lot_data = {
                        "id": lot_id,
                        "techniques": {
                            "frameworkAgreement": {
                                "maximumParticipants": int(max_participants[0])
                            }
                        },
                    }
                    result["tender"]["lots"].append(lot_data)
                except ValueError:
                    logger.warning(
                        "Invalid maximum participants value for lot %s: %s",
                        lot_id,
                        max_participants[0],
                    )
    else:
        # Try legacy TED format
        ted_xpaths = [
            "//ted:FORM_SECTION/*/ted:PROCEDURE/ted:FRAMEWORK/ted:NB_PARTICIPANTS/text()",
            "//ted:FORM_SECTION/ted:CONTRACT_DEFENCE/ted:FD_CONTRACT_DEFENCE/ted:OBJECT_CONTRACT_INFORMATION_DEFENCE/ted:DESCRIPTION_CONTRACT_INFORMATION_DEFENCE/ted:F17_FRAMEWORK/ted:SEVERAL_OPERATORS/ted:MAX_NUMBER_PARTICIPANTS/text()",
            "//ted:FORM_SECTION/ted:CONTRACT_CONCESSIONAIRE_DEFENCE/ted:FD_CONTRACT_CONCESSIONAIRE_DEFENCE/ted:OBJECT_CONTRACT_SUB_DEFENCE/ted:DESCRIPTION_CONTRACT_SUB_DEFENCE/ted:F19_FRAMEWORK/ted:SEVERAL_OPERATORS/ted:MAX_NUMBER_PARTICIPANTS/text()",
        ]

        for xpath in ted_xpaths:
            max_participants = root.xpath(xpath, namespaces=namespaces)
            if max_participants:
                try:
                    lot_data = {
                        "id": "1",  # Legacy TED format typically doesn't have lot IDs
                        "techniques": {
                            "frameworkAgreement": {
                                "maximumParticipants": int(max_participants[0])
                            }
                        },
                    }
                    result["tender"]["lots"].append(lot_data)
                    break  # Use the first found value
                except ValueError:
                    logger.warning(
                        "Invalid maximum participants value in TED format: %s",
                        max_participants[0],
                    )

    return result if result["tender"]["lots"] else None


def merge_framework_max_participants(
    release_json: dict, framework_max_participants_data: dict | None
) -> None:
    """Merge framework maximum participants data into the OCDS release.

    Updates the release JSON in-place by adding or updating framework agreement
    information for each lot specified in the input data.

    Args:
        release_json: The main OCDS release JSON to be updated. Must contain
            a 'tender' object with a 'lots' array.
        framework_max_participants_data: The parsed maximum participants data
            in the same format as returned by parse_framework_max_participants().
            If None, no changes will be made.

    Returns:
        None: The function modifies release_json in-place.

    """
    if not framework_max_participants_data:
        logger.info("No framework maximum participants data to merge")
        return

    tender = release_json.setdefault("tender", {})
    existing_lots = tender.setdefault("lots", [])

    for new_lot in framework_max_participants_data["tender"]["lots"]:
        existing_lot = next(
            (lot for lot in existing_lots if lot["id"] == new_lot["id"]),
            None,
        )
        if existing_lot:
            techniques = existing_lot.setdefault("techniques", {})
            framework = techniques.setdefault("frameworkAgreement", {})
            framework["maximumParticipants"] = new_lot["techniques"][
                "frameworkAgreement"
            ]["maximumParticipants"]
        else:
            existing_lots.append(new_lot)

    logger.info(
        "Merged framework maximum participants data for %d lots",
        len(framework_max_participants_data["tender"]["lots"]),
    )
