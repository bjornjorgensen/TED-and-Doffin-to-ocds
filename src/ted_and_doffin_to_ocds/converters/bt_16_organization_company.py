# converters/bt_16_organization_company.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)


def parse_organization_part_name(xml_content):
    """
    Parse the XML content to extract the organization part name.

    Args:
        xml_content (str): The XML content to parse.

    Returns:
        dict: A dictionary containing the parsed data in the format:
              {
                  "parties": [
                      {
                          "id": "organization_id",
                          "name": "organization_name - department_name"
                      }
                  ]
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

    result = {"parties": []}

    organizations = root.xpath(
        "//efac:organizations/efac:organization",
        namespaces=namespaces,
    )

    for organization in organizations:
        org_id = organization.xpath(
            "efac:company/cac:partyIdentification/cbc:ID[@schemeName='organization']/text()",
            namespaces=namespaces,
        )
        org_name = organization.xpath(
            "efac:company/cac:partyName/cbc:Name/text()",
            namespaces=namespaces,
        )
        department = organization.xpath(
            "efac:company/cac:PostalAddress/cbc:Department/text()",
            namespaces=namespaces,
        )

        if org_id and org_name:
            full_name = org_name[0]
            if department:
                full_name += f" - {department[0]}"

            party = {"id": org_id[0], "name": full_name}
            result["parties"].append(party)

    return result if result["parties"] else None


def merge_organization_part_name(release_json, organization_part_name_data):
    """
    Merge the parsed organization part name data into the main OCDS release JSON.

    Args:
        release_json (dict): The main OCDS release JSON to be updated.
        organization_part_name_data (dict): The parsed organization part name data to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not organization_part_name_data:
        logger.warning("No organization part Name data to merge")
        return

    existing_parties = release_json.setdefault("parties", [])

    for new_party in organization_part_name_data["parties"]:
        existing_party = next(
            (party for party in existing_parties if party["id"] == new_party["id"]),
            None,
        )
        if existing_party:
            existing_party["name"] = new_party["name"]
        else:
            existing_parties.append(new_party)

    logger.info(
        "Merged organization part Name data for %d parties",
        len(organization_part_name_data["parties"]),
    )