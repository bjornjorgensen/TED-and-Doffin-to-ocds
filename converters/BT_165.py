from lxml import etree

def parse_winner_size(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
        'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
        'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
        'efbc': 'http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1',
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = {"parties": []}

    organizations = root.xpath("//efac:Organizations/efac:Organization", namespaces=namespaces)
    
    for org in organizations:
        org_id = org.xpath("efac:Company/cac:PartyIdentification/cbc:ID/text()", namespaces=namespaces)
        company_size = org.xpath("efac:Company/efbc:CompanySizeCode/text()", namespaces=namespaces)
        
        if org_id and company_size:
            party = {
                "id": org_id[0],
                "details": {
                    "scale": company_size[0]
                }
            }
            result["parties"].append(party)

    return result if result["parties"] else None