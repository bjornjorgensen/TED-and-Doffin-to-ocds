from lxml import etree

def parse_buyer_contracting_entity(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = []

    contracting_parties = root.xpath("//cac:ContractingParty", namespaces=namespaces)
    for party in contracting_parties:
        org_id = party.xpath("cac:Party/cac:PartyIdentification/cbc:ID/text()", namespaces=namespaces)
        party_type_code = party.xpath("cac:ContractingPartyType/cbc:PartyTypeCode[@listName='buyer-contracting-type']/text()", namespaces=namespaces)
        
        if org_id and party_type_code:
            result.append({
                'id': org_id[0],
                'type_code': party_type_code[0]
            })

    return result

def merge_buyer_contracting_entity(release_json, buyer_data):
    parties = release_json.setdefault("parties", [])

    buyer_contracting_type_mapping = {
        'cont-ent': 'Contracting Entity',
        'not-cont-ent': 'Not Contracting Entity'
    }

    for buyer in buyer_data:
        org = next((p for p in parties if p.get('id') == buyer['id']), None)
        if not org:
            org = {'id': buyer['id']}
            parties.append(org)

        roles = org.setdefault('roles', [])
        if 'buyer' not in roles:
            roles.append('buyer')

        details = org.setdefault('details', {})
        classifications = details.setdefault('classifications', [])
        
        classifications.append({
            'scheme': 'eu-buyer-contracting-type',
            'id': buyer['type_code'],
            'description': buyer_contracting_type_mapping.get(buyer['type_code'], 'Unknown')
        })

    return release_json