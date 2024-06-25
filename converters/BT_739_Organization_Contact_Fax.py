from lxml import etree

def parse_organization_contact_fax(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
        'efext': 'http://data.europa.eu/p27/eforms-ubl-extension/1',
        'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1'    }

    result = []

    # Organization-Company
    company_faxes = root.xpath("//efac:Organization/efac:Company", namespaces=namespaces)
    for company in company_faxes:
        org_ids = company.xpath("cac:PartyIdentification/cbc:ID/text()", namespaces=namespaces)
        fax = company.xpath("cac:Contact/cbc:Telefax/text()", namespaces=namespaces)
        if org_ids and fax:
            result.append({
                'type': 'company',
                'id': org_ids[0],
                'fax': fax[0]
            })

    # Organization-TouchPoint
    touchpoint_faxes = root.xpath("//efac:Organization/efac:TouchPoint", namespaces=namespaces)
    for touchpoint in touchpoint_faxes:
        tp_ids = touchpoint.xpath("cac:PartyIdentification/cbc:ID/text()", namespaces=namespaces)
        company_ids = touchpoint.xpath("../efac:Company/cac:PartyLegalEntity/cbc:CompanyID/text()", namespaces=namespaces)
        fax = touchpoint.xpath("cac:Contact/cbc:Telefax/text()", namespaces=namespaces)
        if tp_ids and company_ids and fax:
            result.append({
                'type': 'touchpoint',
                'id': tp_ids[0],
                'company_id': company_ids[0],
                'fax': fax[0]
            })

    # UBO
    ubo_faxes = root.xpath("//efac:UltimateBeneficialOwner", namespaces=namespaces)
    for ubo in ubo_faxes:
        ubo_ids = ubo.xpath("cbc:ID/text()", namespaces=namespaces)
        org_ids = ubo.xpath("../efac:Organization/efac:Company/cac:PartyIdentification/cbc:ID/text()", namespaces=namespaces)
        fax = ubo.xpath("cac:Contact/cbc:Telefax/text()", namespaces=namespaces)
        if ubo_ids and org_ids and fax:
            result.append({
                'type': 'ubo',
                'id': ubo_ids[0],
                'org_id': org_ids[0],
                'fax': fax[0]
            })

    return result

def merge_organization_contact_fax(release_json, fax_data):
    parties = release_json.setdefault("parties", [])

    for fax_entry in fax_data:
        if fax_entry['type'] == 'company':
            org = next((p for p in parties if p.get('id') == fax_entry['id']), None)
            if not org:
                org = {'id': fax_entry['id']}
                parties.append(org)
            contact_point = org.setdefault('contactPoint', {})
            contact_point['faxNumber'] = fax_entry['fax']

        elif fax_entry['type'] == 'touchpoint':
            org = next((p for p in parties if p.get('id') == fax_entry['id']), None)
            if not org:
                org = {
                    'id': fax_entry['id'],
                    'identifier': {
                        'id': fax_entry['company_id'],
                        'scheme': 'GB-COH'  # Assuming GB-COH scheme, adjust if needed
                    }
                }
                parties.append(org)
            contact_point = org.setdefault('contactPoint', {})
            contact_point['faxNumber'] = fax_entry['fax']

        elif fax_entry['type'] == 'ubo':
            org = next((p for p in parties if p.get('id') == fax_entry['org_id']), None)
            if not org:
                org = {'id': fax_entry['org_id']}
                parties.append(org)
            beneficial_owners = org.setdefault('beneficialOwners', [])
            ubo = next((bo for bo in beneficial_owners if bo.get('id') == fax_entry['id']), None)
            if not ubo:
                ubo = {'id': fax_entry['id']}
                beneficial_owners.append(ubo)
            ubo['faxNumber'] = fax_entry['fax']

    return release_json