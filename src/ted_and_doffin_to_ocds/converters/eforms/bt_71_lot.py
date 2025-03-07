# converters/bt_71_Lot.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_reserved_participation(xml_content: str | bytes) -> dict | None:
    """Parse reserved participation information from XML for each lot.

    Extracts whether participation is reserved for specific organisations
    (e.g. sheltered workshops, organisations pursuing a public service mission)
    as defined in BT-71.

    Args:
        xml_content: The XML content to parse, either as a string or bytes.

    Returns:
        A dictionary containing the parsed data in OCDS format with the following structure:
        {
            "tender": {
                "lots": [
                    {
                        "id": str,
                        "otherRequirements": {
                            "reservedParticipation": [str]  # List containing either
                                                          # "shelteredWorkshop" or
                                                          # "publicServiceMissionOrganization"
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

    xpath_query = "/*/cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']"
    lots = root.xpath(xpath_query, namespaces=namespaces)

    for lot in lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)
        if not lot_id:
            logger.warning("Lot ID not found")
            continue

        lot_id = lot_id[0]
        xpath_reserved = (
            "cac:TenderingTerms/cac:TendererQualificationRequest"
            "[not(cbc:CompanyLegalFormCode)]"
            "[not(cac:SpecificTendererRequirement/cbc:TendererRequirementTypeCode[@listName='missing-info-submission'])]"
            "[not(cac:SpecificTendererRequirement/cbc:TendererRequirementTypeCode[@listName='selection-criteria-source'])]"
            "/cac:SpecificTendererRequirement[cbc:TendererRequirementTypeCode/@listName='reserved-procurement']/cbc:TendererRequirementTypeCode/text()"
        )
        reserved_code = lot.xpath(xpath_reserved, namespaces=namespaces)

        if reserved_code:
            reserved_type = None
            if reserved_code[0] == "res-pub-ser":
                reserved_type = "publicServiceMissionOrganization"
            elif reserved_code[0] == "res-ws":
                reserved_type = "shelteredWorkshop"

            if reserved_type:
                result["tender"]["lots"].append(
                    {
                        "id": lot_id,
                        "otherRequirements": {"reservedParticipation": [reserved_type]},
                    }
                )

    return result if result["tender"]["lots"] else None


def merge_reserved_participation(
    release_json: dict, reserved_participation_data: dict | None
) -> None:
    """Merge reserved participation data into the OCDS release.

    Updates the release JSON in-place by adding or updating other requirements
    for each lot specified in the input data.

    Args:
        release_json: The main OCDS release JSON to be updated. Must contain
            a 'tender' object with a 'lots' array.
        reserved_participation_data: The parsed reserved participation data
            in the same format as returned by parse_reserved_participation().
            If None, no changes will be made.

    Returns:
        None: The function modifies release_json in-place.

    """
    if not reserved_participation_data:
        logger.warning("No reserved participation data to merge")
        return

    tender = release_json.setdefault("tender", {})
    existing_lots = tender.setdefault("lots", [])

    for new_lot in reserved_participation_data["tender"]["lots"]:
        existing_lot = next(
            (lot for lot in existing_lots if lot["id"] == new_lot["id"]),
            None,
        )
        if existing_lot:
            existing_lot.setdefault("otherRequirements", {}).update(
                new_lot["otherRequirements"],
            )
        else:
            existing_lots.append(new_lot)

    logger.info(
        "Merged reserved participation data for %d lots",
        len(reserved_participation_data["tender"]["lots"]),
    )
