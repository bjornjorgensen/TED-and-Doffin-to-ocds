# converters/BT_633_Organization.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)


def parse_organization_natural_person(xml_content):
    """
    Parse the XML content to extract the natural person indicator for each organization.

    Args:
        xml_content (str): The XML content to parse.

    Returns:
        dict: A dictionary containing the parsed natural person data in the format:
              {
                  "parties": [
                      {
                          "id": "organization_id",
                          "details": {
                              "scale": "selfEmployed"
                          }
                      }
                  ]
              }
        None: If no relevant data is found.

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

    result = {"parties": []}

    organizations = root.xpath(
        "//efac:Organizations/efac:Organization",
        namespaces=namespaces,
    )

    for organization in organizations:
        org_id = organization.xpath(
            "efac:Company/cac:PartyIdentification/cbc:ID[@schemeName='organization']/text()",
            namespaces=namespaces,
        )
        natural_person_indicator = organization.xpath(
            "efbc:NaturalPersonIndicator/text()",
            namespaces=namespaces,
        )

        if (
            org_id
            and natural_person_indicator
            and natural_person_indicator[0].lower() == "true"
        ):
            party = {"id": org_id[0], "details": {"scale": "selfEmployed"}}
            result["parties"].append(party)

    return result if result["parties"] else None


def merge_organization_natural_person(release_json, organization_natural_person_data):
    """
    Merge the parsed natural person data into the main OCDS release JSON.

    Args:
        release_json (dict): The main OCDS release JSON to be updated.
        organization_natural_person_data (dict): The parsed natural person data to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not organization_natural_person_data:
        logger.warning("No Organization Natural Person data to merge")
        return

    existing_parties = release_json.setdefault("parties", [])

    for new_party in organization_natural_person_data["parties"]:
        existing_party = next(
            (party for party in existing_parties if party["id"] == new_party["id"]),
            None,
        )
        if existing_party:
            existing_party.setdefault("details", {}).update(new_party["details"])
        else:
            existing_parties.append(new_party)

    logger.info(
        f"Merged Organization Natural Person data for {len(organization_natural_person_data['parties'])} parties",
    )
