# converters/bt_71_part.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)


def parse_reserved_participation_part(xml_content):
    """
    Parse the XML content to extract reserved participation information for the tender.

    Args:
        xml_content (str): The XML content to parse.

    Returns:
        dict: A dictionary containing the parsed reserved participation data in the format:
              {
                  "tender": {
                      "otherRequirements": {
                          "reservedparticipation": ["participation_type"]
                      }
                  }
              }
        None: If no relevant data is found.
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

    xpath_query = "/*/cac:ProcurementProjectLot[cbc:ID/@schemeName='part']/cac:TenderingTerms/cac:TendererQualificationRequest[not(cbc:companyLegalFormCode)][not(cac:SpecificTendererRequirement/cbc:TendererRequirementTypeCode[@listName='missing-info-submission'])]/cac:SpecificTendererRequirement[cbc:TendererRequirementTypeCode/@listName='reserved-procurement']/cbc:TendererRequirementTypeCode/text()"

    reserved_codes = root.xpath(xpath_query, namespaces=namespaces)

    if reserved_codes:
        reserved_types = set()
        for code in reserved_codes:
            if code == "res-pub-ser":
                reserved_types.add("publicServiceMissionorganization")
            elif code == "res-ws":
                reserved_types.add("shelteredWorkshop")

        if reserved_types:
            return {
                "tender": {
                    "otherRequirements": {
                        "reservedparticipation": list(reserved_types),
                    },
                },
            }

    return None


def merge_reserved_participation_part(release_json, reserved_participation_data):
    """
    Merge the parsed reserved participation data into the main OCDS release JSON.

    Args:
        release_json (dict): The main OCDS release JSON to be updated.
        reserved_participation_data (dict): The parsed reserved participation data to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not reserved_participation_data:
        logger.warning("No reserved participation data to merge")
        return

    tender = release_json.setdefault("tender", {})
    other_requirements = tender.setdefault("otherRequirements", {})

    if (
        "reservedparticipation"
        in reserved_participation_data["tender"]["otherRequirements"]
    ):
        existing_reserved = set(other_requirements.get("reservedparticipation", []))
        new_reserved = set(
            reserved_participation_data["tender"]["otherRequirements"][
                "reservedparticipation"
            ],
        )
        other_requirements["reservedparticipation"] = list(
            existing_reserved.union(new_reserved),
        )

    logger.info("Merged reserved participation data for tender")
