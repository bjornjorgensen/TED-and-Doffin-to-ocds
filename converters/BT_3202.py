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
    
    notice_result = root.xpath("/*/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:NoticeResult", namespaces=namespaces)[0]
    
    # Process SettledContracts
    settled_contracts = notice_result.xpath("efac:SettledContract", namespaces=namespaces)
    for settled_contract in settled_contracts:
        contract_id = settled_contract.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        tender_id = settled_contract.xpath("efac:LotTender/cbc:ID/text()", namespaces=namespaces)[0]
        
        contract = {
            "id": contract_id,
            "relatedBids": [tender_id]
        }
        
        # Find related LotResults
        lot_results = notice_result.xpath(f"efac:LotResult[efac:SettledContract/cbc:ID/text()='{contract_id}']", namespaces=namespaces)
        if len(lot_results) == 1:
            contract["awardID"] = lot_results[0].xpath("cbc:ID/text()", namespaces=namespaces)[0]
        elif len(lot_results) > 1:
            contract["awardIDs"] = [lot_result.xpath("cbc:ID/text()", namespaces=namespaces)[0] for lot_result in lot_results]
        
        result["contracts"].append(contract)
        
        # Process related LotTender and TenderingParty
        lot_tender = notice_result.xpath(f"efac:LotTender[cbc:ID/text()='{tender_id}']", namespaces=namespaces)[0]
        tendering_party_id = lot_tender.xpath("efac:TenderingParty/cbc:ID/text()", namespaces=namespaces)[0]
        tendering_party = notice_result.xpath(f"efac:TenderingParty[cbc:ID/text()='{tendering_party_id}']", namespaces=namespaces)[0]
        
        for tenderer in tendering_party.xpath("efac:Tenderer", namespaces=namespaces):
            org_id = tenderer.xpath("cbc:ID/text()", namespaces=namespaces)[0]
            
            # Add or update organization in parties
            org = next((party for party in result["parties"] if party["id"] == org_id), None)
            if not org:
                org = {"id": org_id, "roles": ["tenderer", "supplier"]}
                result["parties"].append(org)
            else:
                org["roles"] = list(set(org["roles"] + ["tenderer", "supplier"]))
            
            # Process awards
            for lot_result in lot_results:
                award_id = lot_result.xpath("cbc:ID/text()", namespaces=namespaces)[0]
                lot_id = lot_result.xpath("efac:TenderLot/cbc:ID/text()", namespaces=namespaces)[0]
                
                award = next((award for award in result["awards"] if award["id"] == award_id), None)
                if not award:
                    award = {
                        "id": award_id,
                        "suppliers": [{"id": org_id}],
                        "relatedLots": [lot_id]
                    }
                    result["awards"].append(award)
                else:
                    if {"id": org_id} not in award["suppliers"]:
                        award["suppliers"].append({"id": org_id})
                    if lot_id not in award["relatedLots"]:
                        award["relatedLots"].append(lot_id)
    
    return result

def merge_contract_tender_id(release_json, contract_tender_id_data):
    if contract_tender_id_data:
        # Merge parties
        existing_parties = release_json.setdefault("parties", [])
        for new_party in contract_tender_id_data["parties"]:
            existing_party = next((party for party in existing_parties if party["id"] == new_party["id"]), None)
            if existing_party:
                existing_party["roles"] = list(set(existing_party.get("roles", []) + new_party["roles"]))
            else:
                existing_parties.append(new_party)
        
        # Merge awards
        existing_awards = release_json.setdefault("awards", [])
        for new_award in contract_tender_id_data["awards"]:
            existing_award = next((award for award in existing_awards if award["id"] == new_award["id"]), None)
            if existing_award:
                existing_award["suppliers"] = list({supplier["id"]: supplier for supplier in existing_award.get("suppliers", []) + new_award["suppliers"]}.values())
                existing_award["relatedLots"] = list(set(existing_award.get("relatedLots", []) + new_award["relatedLots"]))
            else:
                existing_awards.append(new_award)
        
        # Merge contracts
        existing_contracts = release_json.setdefault("contracts", [])
        for new_contract in contract_tender_id_data["contracts"]:
            existing_contract = next((contract for contract in existing_contracts if contract["id"] == new_contract["id"]), None)
            if existing_contract:
                existing_contract["relatedBids"] = list(set(existing_contract.get("relatedBids", []) + new_contract["relatedBids"]))
                if "awardID" in new_contract:
                    existing_contract["awardID"] = new_contract["awardID"]
                if "awardIDs" in new_contract:
                    existing_contract["awardIDs"] = list(set(existing_contract.get("awardIDs", []) + new_contract["awardIDs"]))
            else:
                existing_contracts.append(new_contract)
