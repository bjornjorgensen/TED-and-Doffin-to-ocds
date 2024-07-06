import logging
from lxml import etree

logger = logging.getLogger(__name__)

def parse_subcontractor_id_reference(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
        'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
        'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1'
    }

    result = {"parties": [], "bids": {"details": []}}

    subcontractors = root.xpath("//efac:NoticeResult/efac:TenderingParty/efac:SubContractor", namespaces=namespaces)
    
    for subcontractor in subcontractors:
        subcontractor_id = subcontractor.xpath("cbc:ID[@schemeName='organization']/text()", namespaces=namespaces)[0]
        
        # Add subcontractor to parties
        result["parties"].append({
            "id": subcontractor_id,
            "roles": ["subcontractor"]
        })

        # Get the bid for the LotTender
        lot_tender = subcontractor.xpath("ancestor::efac:NoticeResult/efac:LotTender", namespaces=namespaces)[0]
        tender_id = lot_tender.xpath("cbc:ID[@schemeName='tender']/text()", namespaces=namespaces)[0]

        # Find or create the bid
        bid = next((b for b in result["bids"]["details"] if b.get("id") == tender_id), None)
        if not bid:
            bid = {"id": tender_id, "subcontracting": {"subcontracts": []}}
            result["bids"]["details"].append(bid)

        # Add subcontract to the bid
        subcontract_id = str(len(bid["subcontracting"]["subcontracts"]) + 1)
        bid["subcontracting"]["subcontracts"].append({
            "id": subcontract_id,
            "subcontractor": {"id": subcontractor_id}
        })

    return result

def merge_subcontractor_id_reference(release_json, subcontractor_data):
    if not subcontractor_data:
        logger.warning("No Subcontractor ID Reference data to merge")
        return

    existing_parties = release_json.setdefault("parties", [])
    for new_party in subcontractor_data["parties"]:
        existing_party = next((party for party in existing_parties if party["id"] == new_party["id"]), None)
        if existing_party:
            existing_party.setdefault("roles", []).extend(role for role in new_party["roles"] if role not in existing_party["roles"])
        else:
            existing_parties.append(new_party)

    existing_bids = release_json.setdefault("bids", {}).setdefault("details", [])
    for new_bid in subcontractor_data["bids"]["details"]:
        existing_bid = next((bid for bid in existing_bids if bid.get("id") == new_bid["id"]), None)
        if existing_bid:
            existing_subcontracts = existing_bid.setdefault("subcontracting", {}).setdefault("subcontracts", [])
            for new_subcontract in new_bid["subcontracting"]["subcontracts"]:
                if not any(sc["subcontractor"]["id"] == new_subcontract["subcontractor"]["id"] for sc in existing_subcontracts):
                    existing_subcontracts.append(new_subcontract)
        else:
            existing_bids.append(new_bid)

    logger.info(f"Merged Subcontractor ID Reference data for {len(subcontractor_data['parties'])} parties and {len(subcontractor_data['bids']['details'])} bids")