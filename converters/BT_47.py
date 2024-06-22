# converters/BT_47.py
from lxml import etree
import uuid

def parse_participant_name(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }
    
    result = {"parties": [], "tender": {"lots": []}}

    lot_elements = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)
    for lot_element in lot_elements:
        lot_id = lot_element.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        
        participant_elements = lot_element.xpath(
            "cac:TenderingTerms/cac:EconomicOperatorShortList/cac:PreSelectedParty/cac:PartyName/cbc:Name",
            namespaces=namespaces
        )
        
        if participant_elements:
            lot = {
                "id": lot_id,
                "designContest": {
                    "selectedParticipants": []
                }
            }
            
            for participant in participant_elements:
                # Generate a unique ID for the participant
                participant_id = str(uuid.uuid4())
                
                # Add to parties array
                result["parties"].append({
                    "id": participant_id,
                    "name": participant.text,
                    "roles": ["selectedParticipant"]
                })
                
                # Add to lot's selectedParticipants array
                lot["designContest"]["selectedParticipants"].append({
                    "id": participant_id,
                    "name": participant.text
                })
            
            result["tender"]["lots"].append(lot)
    
    return result if (result["parties"] and result["tender"]["lots"]) else None

def merge_participant_name(release_json, participant_name_data):
    if participant_name_data:
        # Merge parties
        existing_parties = release_json.setdefault("parties", [])
        for new_party in participant_name_data.get("parties", []):
            existing_party = next((party for party in existing_parties if party["id"] == new_party["id"]), None)
            if existing_party:
                existing_party["name"] = new_party["name"]
                existing_party.setdefault("roles", []).append("selectedParticipant")
            else:
                existing_parties.append(new_party)
        
        # Merge lots
        if "tender" in participant_name_data and "lots" in participant_name_data["tender"]:
            tender = release_json.setdefault("tender", {})
            existing_lots = tender.setdefault("lots", [])
            
            for new_lot in participant_name_data["tender"]["lots"]:
                existing_lot = next((lot for lot in existing_lots if lot["id"] == new_lot["id"]), None)
                if existing_lot:
                    existing_design_contest = existing_lot.setdefault("designContest", {})
                    existing_participants = existing_design_contest.setdefault("selectedParticipants", [])
                    
                    for new_participant in new_lot["designContest"]["selectedParticipants"]:
                        existing_participant = next((p for p in existing_participants if p["id"] == new_participant["id"]), None)
                        if existing_participant:
                            existing_participant.update(new_participant)
                        else:
                            existing_participants.append(new_participant)
                else:
                    existing_lots.append(new_lot)
