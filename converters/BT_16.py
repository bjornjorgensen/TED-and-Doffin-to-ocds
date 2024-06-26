# converters/BT_16.py
from lxml import etree

def parse_organisation_part_name(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
        'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
        'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = {"parties": []}

    organizations = root.xpath("//efac:Organizations/efac:Organization", namespaces=namespaces)
    
    for org in organizations:
        # Parse Company information
        company = org.xpath("efac:Company", namespaces=namespaces)
        if company:
            org_id = company[0].xpath("cac:PartyIdentification/cbc:ID/text()", namespaces=namespaces)
            org_name = company[0].xpath("cac:PartyName/cbc:Name/text()", namespaces=namespaces)
            org_department = company[0].xpath("cac:PostalAddress/cbc:Department/text()", namespaces=namespaces)
            
            if org_id and org_name:
                party = {
                    "id": org_id[0],
                    "name": org_name[0]
                }
                
                if org_department:
                    party["name"] += f" - {org_department[0]}"
                
                result["parties"].append(party)

        # Parse TouchPoint information
        touchpoint = org.xpath("efac:TouchPoint", namespaces=namespaces)
        if touchpoint:
            tp_id = touchpoint[0].xpath("cac:PartyIdentification/cbc:ID/text()", namespaces=namespaces)
            tp_name = touchpoint[0].xpath("cac:PartyName/cbc:Name/text()", namespaces=namespaces)
            tp_department = touchpoint[0].xpath("cac:PostalAddress/cbc:Department/text()", namespaces=namespaces)
            company_id = org.xpath("efac:Company/cac:PartyLegalEntity/cbc:CompanyID/text()", namespaces=namespaces)
            
            if tp_id and tp_name:
                party = {
                    "id": tp_id[0],
                    "name": tp_name[0]
                }
                
                if tp_department:
                    party["name"] += f" - {tp_department[0]}"
                
                if company_id:
                    party["identifier"] = {
                        "id": company_id[0],
                        "scheme": "internal"
                    }
                
                result["parties"].append(party)

    return result if result["parties"] else None