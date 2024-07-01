# converters/OPT_300.py

from lxml import etree

def parse_opt_300(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
        'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
        'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = {"parties": [], "awards": [], "buyer": None}

    # OPT-300-Contract-Signatory
    signatory_parties = root.xpath("//efac:NoticeResult/efac:SettledContract/cac:SignatoryParty/cac:PartyIdentification/cbc:ID", namespaces=namespaces)
    
    for signatory_party in signatory_parties:
        org_id = signatory_party.text
        org_name = root.xpath(f"//efac:Organizations/efac:Organization/efac:Company[cac:PartyIdentification/cbc:ID/text()='{org_id}']/cac:PartyName/cbc:Name/text()", namespaces=namespaces)
        
        party = {
            "id": org_id,
            "roles": ["buyer"]
        }
        if org_name:
            party["name"] = org_name[0]
        
        result["parties"].append(party)

        # Find related contracts and awards
        contracts = root.xpath(f"//efac:NoticeResult/efac:SettledContract[cac:SignatoryParty/cac:PartyIdentification/cbc:ID/text()='{org_id}']", namespaces=namespaces)
        for contract in contracts:
            contract_id = contract.xpath("cbc:ID[@schemeName='contract']/text()", namespaces=namespaces)
            if contract_id:
                award_ids = root.xpath(f"//efac:NoticeResult/efac:LotResult[efac:SettledContract/cbc:ID[@schemeName='contract']/text()='{contract_id[0]}']/cbc:ID[@schemeName='result']/text()", namespaces=namespaces)
                for award_id in award_ids:
                    result["awards"].append({
                        "id": award_id,
                        "buyers": [{"id": org_id}]
                    })

    # OPT-300-Procedure-Buyer
    buyer_ids = root.xpath("//cac:ContractingParty/cac:Party/cac:PartyIdentification/cbc:ID/text()", namespaces=namespaces)
    
    for buyer_id in buyer_ids:
        existing_party = next((party for party in result["parties"] if party["id"] == buyer_id), None)
        if existing_party:
            if "buyer" not in existing_party["roles"]:
                existing_party["roles"].append("buyer")
        else:
            result["parties"].append({
                "id": buyer_id,
                "roles": ["buyer"]
            })
        
        result["buyer"] = {"id": buyer_id}

    # OPT-300-Procedure-SProvider
    service_provider_ids = root.xpath("//cac:ContractingParty/cac:Party/cac:ServiceProviderParty/cac:Party/cac:PartyIdentification/cbc:ID/text()", namespaces=namespaces)
    
    for sp_id in service_provider_ids:
        org_name = root.xpath(f"//efac:Organizations/efac:Organization/efac:Company[cac:PartyIdentification/cbc:ID/text()='{sp_id}']/cac:PartyName/cbc:Name/text()", namespaces=namespaces)
        
        existing_party = next((party for party in result["parties"] if party["id"] == sp_id), None)
        if existing_party:
            if org_name and "name" not in existing_party:
                existing_party["name"] = org_name[0]
        else:
            party = {"id": sp_id}
            if org_name:
                party["name"] = org_name[0]
            result["parties"].append(party)

    return result

def merge_opt_300(release_json, opt_300_data):
    if not opt_300_data:
        return

    parties = release_json.setdefault("parties", [])
    awards = release_json.setdefault("awards", [])

    for new_party in opt_300_data["parties"]:
        existing_party = next((party for party in parties if party["id"] == new_party["id"]), None)
        if existing_party:
            existing_party.update(new_party)
        else:
            parties.append(new_party)

    for new_award in opt_300_data["awards"]:
        existing_award = next((award for award in awards if award["id"] == new_award["id"]), None)
        if existing_award:
            existing_buyers = existing_award.setdefault("buyers", [])
            for new_buyer in new_award["buyers"]:
                if new_buyer not in existing_buyers:
                    existing_buyers.append(new_buyer)
        else:
            awards.append(new_award)

    if opt_300_data["buyer"]:
        release_json["buyer"] = opt_300_data["buyer"]