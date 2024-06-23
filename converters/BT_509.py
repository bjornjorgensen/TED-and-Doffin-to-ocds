# converters/BT_509.py
from lxml import etree

def parse_edelivery_gateway(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
        'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
        'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1'
    }
    
    result = {"parties": []}

    # Parse Company eDelivery Gateway
    company_elements = root.xpath("//efac:Organizations/efac:Organization/efac:Company", namespaces=namespaces)
    for company in company_elements:
        org_id = company.xpath("cac:PartyIdentification/cbc:ID/text()", namespaces=namespaces)[0]
        endpoint_id = company.xpath("cbc:EndpointID/text()", namespaces=namespaces)
        
        if endpoint_id:
            party = {
                "id": org_id,
                "eDeliveryGateway": endpoint_id[0]
            }
            result["parties"].append(party)

    # Parse TouchPoint eDelivery Gateway
    touchpoint_elements = root.xpath("//efac:Organizations/efac:Organization/efac:TouchPoint", namespaces=namespaces)
    for touchpoint in touchpoint_elements:
        org_id = touchpoint.xpath("cac:PartyIdentification/cbc:ID/text()", namespaces=namespaces)[0]
        endpoint_id = touchpoint.xpath("cbc:EndpointID/text()", namespaces=namespaces)
        company_id = touchpoint.xpath("../efac:Company/cac:PartyLegalEntity/cbc:CompanyID/text()", namespaces=namespaces)
        
        if endpoint_id:
            party = {
                "id": org_id,
                "eDeliveryGateway": endpoint_id[0]
            }
            if company_id:
                party["identifier"] = {
                    "id": company_id[0],
                    "scheme": "internal"
                }
            result["parties"].append(party)

    return result if result["parties"] else None

def merge_edelivery_gateway(release_json, edelivery_gateway_data):
    if edelivery_gateway_data and "parties" in edelivery_gateway_data:
        existing_parties = release_json.setdefault("parties", [])
        
        for new_party in edelivery_gateway_data["parties"]:
            existing_party = next((party for party in existing_parties if party["id"] == new_party["id"]), None)
            if existing_party:
                # Update existing party
                existing_party["eDeliveryGateway"] = new_party["eDeliveryGateway"]
                if "identifier" in new_party:
                    existing_party["identifier"] = new_party["identifier"]
            else:
                # Add new party
                existing_parties.append(new_party)
