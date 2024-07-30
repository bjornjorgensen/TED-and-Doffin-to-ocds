# converters/OPT_301_Tenderer_MainCont.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)

def parse_tenderer_maincont(xml_content):
    if isinstance(xml_content, str):
        xml_content = xml_content.encode('utf-8')
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
        'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
        'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1'
    }

    result = {"parties": [], "bids": {"details": []}}

    xpath = "/*/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:NoticeResult/efac:TenderingParty/efac:SubContractor"
    subcontractors = root.xpath(xpath, namespaces=namespaces)

    for subcontractor in subcontractors:
        subcontractor_id = subcontractor.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        main_contractor_id = subcontractor.xpath("efac:MainContractor/cbc:ID/text()", namespaces=namespaces)[0]

        # Add main contractor to parties
        result["parties"].append({
            "id": main_contractor_id,
            "roles": ["tenderer"]
        })

        # Get main contractor name
        main_contractor_name_xpath = f"//efac:Organizations/efac:Organization/efac:Company[cac:PartyIdentification/cbc:ID/text()='{main_contractor_id}']/cac:PartyName/cbc:Name/text()"
        main_contractor_name = root.xpath(main_contractor_name_xpath, namespaces=namespaces)
        main_contractor_name = main_contractor_name[0] if main_contractor_name else None

        # Add subcontract to bids
        bid = next((bid for bid in result["bids"]["details"] if "subcontracting" in bid), None)
        if not bid:
            bid = {"subcontracting": {"subcontracts": []}}
            result["bids"]["details"].append(bid)

        subcontract = {
            "id": str(len(bid["subcontracting"]["subcontracts"]) + 1),
            "subcontractor": {"id": subcontractor_id},
            "mainContractors": [{
                "id": main_contractor_id
            }]
        }
        if main_contractor_name:
            subcontract["mainContractors"][0]["name"] = main_contractor_name

        bid["subcontracting"]["subcontracts"].append(subcontract)

    return result if (result["parties"] or result["bids"]["details"]) else None

def merge_tenderer_maincont(release_json, maincont_data):
    if not maincont_data:
        logger.warning("No Tenderer Main Contractor data to merge")
        return

    # Merge parties
    existing_parties = {party["id"]: party for party in release_json.get("parties", [])}
    for party in maincont_data["parties"]:
        if party["id"] in existing_parties:
            existing_roles = set(existing_parties[party["id"]].get("roles", []))
            existing_roles.update(party["roles"])
            existing_parties[party["id"]]["roles"] = list(existing_roles)
        else:
            release_json.setdefault("parties", []).append(party)

    # Merge bids
    if "bids" not in release_json:
        release_json["bids"] = {"details": []}

    existing_bids = {bid.get("id"): bid for bid in release_json["bids"]["details"] if "id" in bid}
    
    for bid in maincont_data["bids"]["details"]:
        if "subcontracting" in bid:
            # This is the subcontracting information
            for existing_bid in release_json["bids"]["details"]:
                if "id" in existing_bid:
                    existing_bid.update(bid)
                    break
            else:
                release_json["bids"]["details"].append(bid)
        elif bid.get("id") in existing_bids:
            # This is a bid with an ID that already exists
            existing_bids[bid["id"]].update(bid)
        else:
            # This is a new bid
            release_json["bids"]["details"].append(bid)

    logger.info(f"Merged Tenderer Main Contractor data for {len(maincont_data['parties'])} parties and {len(maincont_data['bids']['details'])} bids")