# converters/bt_71_part.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)

# Constants for code mapping
RESERVED_CODE_MAPPING = {
    "res-pub-ser": "publicServiceMissionOrganization",
    "res-ws": "shelteredWorkshop",
}


def parse_reserved_participation_part(xml_content: str | bytes) -> dict | None:
    """Parse reserved participation information from XML.

    Extracts whether participation is reserved for specific organisations
    (e.g. sheltered workshops, organisations pursuing a public service mission)
    as defined in BT-71.

    Args:
        xml_content: The XML content to parse, either as a string or bytes.

    Returns:
        A dictionary containing the parsed data in OCDS format with the following structure:
        {
            "tender": {
                "otherRequirements": {
                    "reservedParticipation": [str]  # List containing either
                                                  # "shelteredWorkshop" or
                                                  # "publicServiceMissionOrganization"
                }
            }
        }
        Returns None if no relevant data is found.

    Raises:
        etree.XMLSyntaxError: If the input is not valid XML.
    """
    if not xml_content:
        return None

    try:
        if isinstance(xml_content, str):
            xml_content = xml_content.encode("utf-8")
        root = etree.fromstring(xml_content)
    except (etree.XMLSyntaxError, ValueError):
        logger.warning("Invalid XML content provided")
        return None

    namespaces = {
        "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
        "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
        "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
        "efext": "http://data.europa.eu/p27/eforms-ubl-extensions/1",
        "efbc": "http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1",
    }

    xpath_query = (
        "/*/cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']"
        "/cac:TenderingTerms/cac:TendererQualificationRequest"
        "[not(cbc:CompanyLegalFormCode)]"
        "[not(cac:SpecificTendererRequirement/cbc:TendererRequirementTypeCode"
        "[@listName='missing-info-submission'])]"
        "[not(cac:SpecificTendererRequirement/cbc:TendererRequirementTypeCode"
        "[@listName='selection-criteria-source'])]"
        "/cac:SpecificTendererRequirement"
        "[cbc:TendererRequirementTypeCode/@listName='reserved-procurement']"
        "/cbc:TendererRequirementTypeCode/text()"
    )

    try:
        reserved_codes = root.xpath(xpath_query, namespaces=namespaces)
    except etree.XPathError:
        logger.warning("Invalid XPath query or namespace")
        return None

    if reserved_codes:
        reserved_types = set()
        for code in reserved_codes:
            if code in RESERVED_CODE_MAPPING:
                reserved_types.add(RESERVED_CODE_MAPPING[code])

        if reserved_types:
            return {
                "tender": {
                    "otherRequirements": {
                        "reservedParticipation": list(reserved_types),
                    },
                },
            }

    return None


def merge_reserved_participation_part(
    release_json: dict, reserved_participation_data: dict | None
) -> None:
    """Merge reserved participation data into the OCDS release.

    Updates the release JSON in-place by adding or updating other requirements.

    Args:
        release_json: The main OCDS release JSON to be updated.
        reserved_participation_data: The parsed reserved participation data
            in the same format as returned by parse_reserved_participation_part().
            If None, no changes will be made.

    Returns:
        None: The function modifies release_json in-place.
    """
    if not reserved_participation_data:
        logger.warning("No reserved participation data to merge")
        return

    tender = release_json.setdefault("tender", {})
    other_requirements = tender.setdefault("otherRequirements", {})

    if (
        "reservedParticipation"
        in reserved_participation_data["tender"]["otherRequirements"]
    ):
        existing_reserved = set(other_requirements.get("reservedParticipation", []))
        new_reserved = set(
            reserved_participation_data["tender"]["otherRequirements"][
                "reservedParticipation"
            ],
        )
        other_requirements["reservedParticipation"] = list(
            existing_reserved.union(new_reserved),
        )

    logger.info("Merged reserved participation data for tender")
