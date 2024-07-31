# converters/BT_510c_Organization_Company.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)

def parse_organization_streetline2(xml_content):
    """
    Parse the XML content to extract the street address information for each organization.

    This function processes the BT-510(c)-Organization-Company business term, which represents
    the full street address of the organization's physical location.

    Args:
        xml_content (str): The XML content to parse.

    Returns:
        dict: A dictionary containing the parsed street address data in the format:
              {
                  "parties": [
                      {
                          "id": "organization_id",
                          "address": {
                              "streetAddress": "full_street_address"
                          }
                      }
                  ]
              }
        None: If no relevant data is found.

    Raises:
        etree.XMLSyntaxError: If the input is not valid XML.
    """
    root = etree.fromstring(xml_content)
    namespaces = {
    'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
    'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
    'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
    'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
    'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
    'efbc': 'http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1'
}

    result = {"parties": []}

    organizations = root.xpath("//efac:Organizations/efac:Organization", namespaces=namespaces)
    
    for organization in organizations:
        org_id = organization.xpath("efac:Company/cac:PartyIdentification/cbc:ID[@schemeName='organization']/text()", namespaces=namespaces)
        
        if org_id:
            street_name = organization.xpath("efac:Company/cac:PostalAddress/cbc:StreetName/text()", namespaces=namespaces)
            additional_street_name = organization.xpath("efac:Company/cac:PostalAddress/cbc:AdditionalStreetName/text()", namespaces=namespaces)
            address_lines = organization.xpath("efac:Company/cac:PostalAddress/cac:AddressLine/cbc:Line/text()", namespaces=namespaces)
            
            street_address_parts = []
            if street_name:
                street_address_parts.append(street_name[0])
            if additional_street_name:
                street_address_parts.append(additional_street_name[0])
            street_address_parts.extend(address_lines)
            
            street_address = ", ".join(street_address_parts)
            
            if street_address:
                party = {
                    "id": org_id[0],
                    "address": {
                        "streetAddress": street_address
                    }
                }
                result["parties"].append(party)

    return result if result["parties"] else None

def merge_organization_streetline2(release_json, organization_streetline2_data):
    """
    Merge the parsed street address data into the main OCDS release JSON.

    This function updates the existing parties in the release JSON with the
    street address information. If a party doesn't exist, it adds a new party to the release.

    Args:
        release_json (dict): The main OCDS release JSON to be updated.
        organization_streetline2_data (dict): The parsed street address data to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not organization_streetline2_data:
        logger.warning("No Organization Streetline 2 data to merge")
        return

    existing_parties = release_json.setdefault("parties", [])
    
    for new_party in organization_streetline2_data["parties"]:
        existing_party = next((party for party in existing_parties if party["id"] == new_party["id"]), None)
        if existing_party:
            existing_party.setdefault("address", {}).update(new_party["address"])
        else:
            existing_parties.append(new_party)

    logger.info(f"Merged Organization Streetline 2 data for {len(organization_streetline2_data['parties'])} parties")