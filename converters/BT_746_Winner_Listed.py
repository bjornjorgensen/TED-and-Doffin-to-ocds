from lxml import etree

def parse_winner_listed(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
        'efext': 'http://data.europa.eu/p27/eforms-ubl-extension/1',
        'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
        'efbc': 'http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1'
    }

    result = []

    organizations = root.xpath("//efac:Organization", namespaces=namespaces)
    for org in organizations:
        org_id = org.xpath("efac:Company/cac:PartyIdentification/cbc:ID/text()", namespaces=namespaces)
        listed_indicator = org.xpath("efbc:ListedOnRegulatedMarketIndicator/text()", namespaces=namespaces)
        
        if org_id and listed_indicator:
            result.append({
                'id': org_id[0],
                'listed': listed_indicator[0].lower() == 'true'
            })

    return result

def merge_winner_listed(release_json, winner_listed_data):
    parties = release_json.setdefault("parties", [])

    for winner in winner_listed_data:
        party = next((p for p in parties if p.get('id') == winner['id']), None)
        if not party:
            party = {'id': winner['id']}
            parties.append(party)

        details = party.setdefault('details', {})
        details['listedOnRegulatedMarket'] = winner['listed']

    return release_json