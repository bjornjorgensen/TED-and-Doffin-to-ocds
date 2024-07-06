import logging
from lxml import etree

logger = logging.getLogger(__name__)

def parse_main_contractor_id_reference(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
        'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
        'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1'
    }

    result = {"parties": [], "bids": {"details": []}}

    main_contractors = root.xpath("//efac:NoticeResult/efac:TenderingParty/efac:SubContractor/efac:MainContractor", namespaces=namespaces)
    
    for main_contractor in main_contractors:
        main_contractor_id = main_contractor.xpath("cbc:ID[@schemeName='organization']/text()", namespaces=namespaces)[0]
        subcontractor_id = main_contractor.xpath("ancestor::efac:SubContractor/cbc:ID[@schemeName='organization']/text()", namespaces=namespaces)[0]
        
        # Add main contractor to parties
        result["parties"].append({
            "id": main_contractor_id,
            "roles": ["tenderer"]
        })

        # Get the bid for the LotTender
        lot_tender = main_contractor.xpath("ancestor::efac:NoticeResult/efac:LotTender", namespaces=namespaces)[0]
        tender_id = lot_tender.xpath("cbc:ID[@schemeName='tender']/text()", namespaces=namespaces)[0]

        # Find or create the bid
        bid = next((b for b in result["bids"]["details"] if b.get("id") == tender_id), None)
        if not bid:
            bid = {"id": tender_id, "subcontracting": {"subcontracts": []}}
            result["bids"]["details"].append(bid)

        # Find or create the subcontract
        subcontract = next((sc for sc in bid["subcontracting"]["subcontracts"] if sc["subcontractor"]["id"] == subcontractor_id), None)
        if not subcontract:
            subcontract = {
                "id": str(len(bid["subcontracting"]["subcontracts"]) + 1),
                "subcontractor": {"id": subcontractor_id},
                "mainContractors": []
            }
            bid["subcontracting"]["subcontracts"].append(subcontract)

        # Add main contractor to the subcontract
        subcontract["mainContractors"].append({
            "id": main_contractor_id,
            "name": main_contractor.xpath("ancestor::efac:Organization/efac:Company/cac:PartyName/cbc:Name/text()", namespaces=namespaces)[0] if main_contractor.xpath("ancestor::efac:Organization/efac:Company/cac:PartyName/cbc:Name", namespaces=namespaces) else None
        })

    return result

def merge_main_contractor_id_reference(release_json, main_contractor_data):
    if not main_contractor_data:
        logger.warning("No Main Contractor ID Reference data to merge")
        return

    existing_parties = release_json.setdefault("parties", [])
    for new_party in main_contractor_data["parties"]:
        existing_party = next((party for party in existing_parties if party["id"] == new_party["id"]), None)
        if existing_party:
            existing_party.setdefault("roles", []).extend(role for role in new_party["roles"] if role not in existing_party["roles"])
        else:
            existing_parties.append(new_party)

    existing_bids = release_json.setdefault("bids", {}).setdefault("details", [])
    for new_bid in main_contractor_data["bids"]["details"]:
        existing_bid = next((bid for bid in existing_bids if bid.get("id") == new_bid["id"]), None)
        if existing_bid:
            existing_subcontracts = existing_bid.setdefault("subcontracting", {}).setdefault("subcontracts", [])
            for new_subcontract in new_bid["subcontracting"]["subcontracts"]:
                existing_subcontract = next((sc for sc in existing_subcontracts if sc["subcontractor"]["id"] == new_subcontract["subcontractor"]["id"]), None)
                if existing_subcontract:
                    existing_subcontract.setdefault("mainContractors", []).extend(
                        mc for mc in new_subcontract["mainContractors"] 
                        if not any(existing_mc["id"] == mc["id"] for existing_mc in existing_subcontract.get("mainContractors", []))
                    )
                else:
                    existing_subcontracts.append(new_subcontract)
        else:
            existing_bids.append(new_bid)

    logger.info(f"Merged Main Contractor ID Reference data for {len(main_contractor_data['parties'])} parties and {len(main_contractor_data['bids']['details'])} bids")