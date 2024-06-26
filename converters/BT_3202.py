# converters/BT_3202.py
from lxml import etree

def parse_contract_tender_id(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
        'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
        'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }
    
    result = {
        "parties": [],
        "awards": [],
        "contracts": []
    }
    
    notice_result = root.xpath("/*/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:NoticeResult", namespaces=namespaces)
    
    if not notice_result:
        return result
    
    notice_result = notice_result[0]
    
    settled_contracts = notice_result.xpath("efac:SettledContract", namespaces=namespaces)
    for settled_contract in settled_contracts:
        contract_id = settled_contract.xpath("cbc:ID/text()", namespaces=namespaces)
        tender_id = settled_contract.xpath("efac:LotTender/cbc:ID/text()", namespaces=namespaces)
        
        if contract_id and tender_id:
            contract = {
                "id": contract_id[0],
                "relatedBids": [tender_id[0]]
            }
            result["contracts"].append(contract)
            
            lot_tender = notice_result.xpath(f"efac:LotTender[cbc:ID/text()='{tender_id[0]}']", namespaces=namespaces)
            if lot_tender:
                tendering_party_id = lot_tender[0].xpath("efac:TenderingParty/cbc:ID/text()", namespaces=namespaces)
                if tendering_party_id:
                    tendering_party = notice_result.xpath(f"efac:TenderingParty[cbc:ID/text()='{tendering_party_id[0]}']", namespaces=namespaces)
                    if tendering_party:
                        tenderers = tendering_party[0].xpath("efac:Tenderer", namespaces=namespaces)
                        for tenderer in tenderers:
                            org_id = tenderer.xpath("cbc:ID/text()", namespaces=namespaces)
                            if org_id:
                                party = {
                                    "id": org_id[0],
                                    "roles": ["supplier"]
                                }
                                result["parties"].append(party)
                                
                                lot_results = notice_result.xpath(f"efac:LotResult[efac:SettledContract/cbc:ID/text()='{contract_id[0]}']", namespaces=namespaces)
                                for lot_result in lot_results:
                                    award_id = lot_result.xpath("cbc:ID/text()", namespaces=namespaces)
                                    lot_id = lot_result.xpath("efac:TenderLot/cbc:ID/text()", namespaces=namespaces)
                                    if award_id:
                                        award = {
                                            "id": award_id[0],
                                            "suppliers": [{"id": org_id[0]}],
                                            "relatedLots": lot_id
                                        }
                                        result["awards"].append(award)
    
    return result

def merge_contract_tender_id(release_json, contract_tender_id_data):
    if not contract_tender_id_data:
        return release_json

    # Merge parties
    existing_parties = release_json.setdefault("parties", [])
    for new_party in contract_tender_id_data.get("parties", []):
        existing_party = next((party for party in existing_parties if party.get("id") == new_party.get("id")), None)
        if existing_party:
            existing_party["roles"] = list(set(existing_party.get("roles", []) + new_party.get("roles", [])))
        else:
            existing_parties.append(new_party)

    # Merge awards
    existing_awards = release_json.setdefault("awards", [])
    for new_award in contract_tender_id_data.get("awards", []):
        existing_award = next((award for award in existing_awards if award.get("id") == new_award.get("id")), None)
        if existing_award:
            existing_award["suppliers"] = list({s.get("id"): s for s in existing_award.get("suppliers", []) + new_award.get("suppliers", [])}.values())
            existing_award["relatedLots"] = list(set(existing_award.get("relatedLots", []) + new_award.get("relatedLots", [])))
        else:
            existing_awards.append(new_award)

    # Merge contracts
    existing_contracts = release_json.setdefault("contracts", [])
    for new_contract in contract_tender_id_data.get("contracts", []):
        existing_contract = next((contract for contract in existing_contracts if contract.get("id") == new_contract.get("id")), None)
        if existing_contract:
            existing_contract["relatedBids"] = list(set(existing_contract.get("relatedBids", []) + new_contract.get("relatedBids", [])))
        else:
            existing_contracts.append(new_contract)

    return release_json