# converters/BT_16_Organization_TouchPoint.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)

def parse_organization_touchpoint_part_name(xml_content):
    """
    Parse the XML content to extract the organization touchpoint part name.

    Args:
        xml_content (str): The XML content to parse.

    Returns:
        dict: A dictionary containing the parsed data in the format:
              {
                  "parties": [
                      {
                          "id": "touchpoint_id",
                          "name": "organization_name - department_name",
                          "identifier": {
                              "id": "company_id",
                              "scheme": "internal"
                          }
                      }
                  ]
              }
        None: If no relevant data is found.
    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode('utf-8')
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
        company_id = organization.xpath("efac:Company/cac:PartyLegalEntity/cbc:CompanyID/text()", namespaces=namespaces)
        touchpoint = organization.xpath("efac:TouchPoint", namespaces=namespaces)
        
        if touchpoint:
            touchpoint_id = touchpoint[0].xpath("cac:PartyIdentification/cbc:ID[@schemeName='touchpoint']/text()", namespaces=namespaces)
            org_name = touchpoint[0].xpath("cac:PartyName/cbc:Name/text()", namespaces=namespaces)
            department = touchpoint[0].xpath("cac:PostalAddress/cbc:Department/text()", namespaces=namespaces)
            
            if touchpoint_id and org_name:
                full_name = org_name[0]
                if department:
                    full_name += f" - {department[0]}"
                
                party = {
                    "id": touchpoint_id[0],
                    "name": full_name,
                    "identifier": {
                        "id": company_id[0] if company_id else None,
                        "scheme": "internal"
                    }
                }
                result["parties"].append(party)

    return result if result["parties"] else None

def merge_organization_touchpoint_part_name(release_json, organization_touchpoint_part_name_data):
    """
    Merge the parsed organization touchpoint part name data into the main OCDS release JSON.

    Args:
        release_json (dict): The main OCDS release JSON to be updated.
        organization_touchpoint_part_name_data (dict): The parsed organization touchpoint part name data to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not organization_touchpoint_part_name_data:
        logger.warning("No Organization TouchPoint Part Name data to merge")
        return

    existing_parties = release_json.setdefault("parties", [])
    
    for new_party in organization_touchpoint_part_name_data["parties"]:
        existing_party = next((party for party in existing_parties if party["id"] == new_party["id"]), None)
        if existing_party:
            existing_party.update(new_party)
        else:
            existing_parties.append(new_party)

    logger.info(f"Merged Organization TouchPoint Part Name data for {len(organization_touchpoint_part_name_data['parties'])} parties")