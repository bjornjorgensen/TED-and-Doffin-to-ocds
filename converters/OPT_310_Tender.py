# converters/OPT_310_Tender.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)

def parse_tendering_party_id_reference(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
        'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
        'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = {"parties": [], "bids": {"details": []}}
    lot_tenders = root.xpath("//efac:NoticeResult/efac:LotTender", namespaces=namespaces)

    for lot_tender in lot_tenders:
        tender_id = lot_tender.xpath("cbc:ID[@schemeName='tender']/text()", namespaces=namespaces)[0]
        tendering_party_ids = lot_tender.xpath("efac:TenderingParty/cbc:ID/text()", namespaces=namespaces)
        
        bid = {"id": tender_id, "tenderers": []}
        
        if tendering_party_ids:
            tendering_party_id = tendering_party_ids[0]
            tendering_party = root.xpath(f"//efac:NoticeResult/efac:TenderingParty[cbc:ID/text()='{tendering_party_id}']", namespaces=namespaces)
            
            if tendering_party:
                tenderers = tendering_party[0].xpath("efac:Tenderer", namespaces=namespaces)
                
                for tenderer in tenderers:
                    org_id = tenderer.xpath("cbc:ID[@schemeName='organization']/text()", namespaces=namespaces)
                    
                    if org_id:
                        org_id = org_id[0]
                        
                        # Add or update party
                        party = next((p for p in result["parties"] if p["id"] == org_id), None)
                        if not party:
                            party = {"id": org_id, "roles": ["tenderer"]}
                            result["parties"].append(party)
                        elif "tenderer" not in party["roles"]:
                            party["roles"].append("tenderer")

                        # Add tenderer to bid
                        bid["tenderers"].append({"id": org_id})

        result["bids"]["details"].append(bid)

    return result if (result["parties"] or result["bids"]["details"]) else None

def merge_tendering_party_id_reference(release_json, tendering_party_data):
    if not tendering_party_data:
        logger.warning("No Tendering Party ID Reference data to merge")
        return

    # Merge parties
    if "parties" not in release_json:
        release_json["parties"] = []
    for new_party in tendering_party_data["parties"]:
        existing_party = next((p for p in release_json["parties"] if p["id"] == new_party["id"]), None)
        if existing_party:
            existing_party["roles"] = list(set(existing_party.get("roles", []) + new_party["roles"]))
        else:
            release_json["parties"].append(new_party)

    # Merge bids
    if "bids" not in release_json:
        release_json["bids"] = {"details": []}
    for new_bid in tendering_party_data["bids"]["details"]:
        existing_bid = next((b for b in release_json["bids"]["details"] if b["id"] == new_bid["id"]), None)
        if existing_bid:
            existing_bid["tenderers"] = new_bid["tenderers"]
        else:
            release_json["bids"]["details"].append(new_bid)

    logger.info(f"Merged Tendering Party ID Reference data for {len(tendering_party_data['bids']['details'])} bids")