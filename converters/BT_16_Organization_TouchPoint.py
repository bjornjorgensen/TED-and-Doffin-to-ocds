# converters/BT_16_Organization_TouchPoint.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)

def parse_touchpoint_part_name(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
        'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
        'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1'
    }

    organizations = []

    org_elements = root.xpath("//efac:Organizations/efac:Organization", namespaces=namespaces)
    
    for org in org_elements:
        touchpoint_id = org.xpath("efac:TouchPoint/cac:PartyIdentification/cbc:ID[@schemeName='touchpoint']/text()", namespaces=namespaces)
        touchpoint_name = org.xpath("efac:TouchPoint/cac:PartyName/cbc:Name/text()", namespaces=namespaces)
        department = org.xpath("efac:TouchPoint/cac:PostalAddress/cbc:Department/text()", namespaces=namespaces)
        company_id = org.xpath("efac:Company/cac:PartyLegalEntity/cbc:CompanyID/text()", namespaces=namespaces)
        
        if touchpoint_id and touchpoint_name:
            full_name = touchpoint_name[0]
            if department:
                full_name += f" - {department[0]}"
            
            party = {
                "id": touchpoint_id[0],
                "name": full_name
            }
            
            if company_id:
                party["identifier"] = {
                    "id": company_id[0],
                    "scheme": "internal"
                }
            
            organizations.append(party)

    logger.info(f"Parsed TouchPoint Part Name data: {organizations}")
    return {"parties": organizations} if organizations else None

def merge_touchpoint_part_name(release_json, touchpoint_part_name_data):
    if not touchpoint_part_name_data:
        logger.warning("No TouchPoint Part Name data to merge")
        return

    existing_parties = release_json.setdefault("parties", [])
    
    for new_org in touchpoint_part_name_data["parties"]:
        existing_org = next((org for org in existing_parties if org["id"] == new_org["id"]), None)
        if existing_org:
            if " - " not in existing_org["name"]:
                existing_org["name"] = new_org["name"]
            if "identifier" not in existing_org and "identifier" in new_org:
                existing_org["identifier"] = new_org["identifier"]
        else:
            existing_parties.append(new_org)

    logger.info(f"Merged TouchPoint Part Name data for {len(touchpoint_part_name_data['parties'])} organizations")
    logger.debug(f"Release JSON after merging TouchPoint Part Name data: {release_json}")