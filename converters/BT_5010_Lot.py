# converters/BT_5010_Lot.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)

def parse_eu_funds_financing_identifier(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
    'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
    'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
    'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
    'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
    'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
    'efbc': 'http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1'
}

    result = {
        "parties": [],
        "planning": {
            "budget": {
                "finance": []
            }
        }
    }

    lots = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)
    
    for lot in lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        funding_elements = lot.xpath(".//efac:Funding", namespaces=namespaces)
        
        for funding in funding_elements:
            financing_identifier = funding.xpath("efbc:FinancingIdentifier/text()", namespaces=namespaces)
            
            if financing_identifier:
                finance_item = {
                    "id": financing_identifier[0],
                    "financingParty": {
                        "name": "European Union"
                    },
                    "relatedLots": [lot_id]
                }
                result["planning"]["budget"]["finance"].append(finance_item)

    if result["planning"]["budget"]["finance"]:
        result["parties"].append({
            "name": "European Union",
            "roles": ["funder"]
        })

    return result if result["parties"] else None

def merge_eu_funds_financing_identifier(release_json, eu_funds_financing_identifier_data):
    if not eu_funds_financing_identifier_data:
        logger.warning("No EU Funds Financing Identifier data to merge")
        return

    existing_parties = release_json.setdefault("parties", [])
    eu_party = next((party for party in existing_parties if party.get("name") == "European Union"), None)

    if eu_party:
        if "funder" not in eu_party.get("roles", []):
            eu_party.setdefault("roles", []).append("funder")
    else:
        new_party = eu_funds_financing_identifier_data["parties"][0]
        new_party["id"] = str(len(existing_parties) + 1)
        existing_parties.append(new_party)

    eu_party = next(party for party in existing_parties if party.get("name") == "European Union")

    planning = release_json.setdefault("planning", {})
    budget = planning.setdefault("budget", {})
    existing_finance = budget.setdefault("finance", [])

    for new_finance in eu_funds_financing_identifier_data["planning"]["budget"]["finance"]:
        existing_finance_item = next((item for item in existing_finance if item["id"] == new_finance["id"]), None)
        if existing_finance_item:
            existing_finance_item["financingParty"] = {
                "id": eu_party["id"],
                "name": "European Union"
            }
            existing_finance_item.setdefault("relatedLots", []).extend(new_finance["relatedLots"])
            existing_finance_item["relatedLots"] = list(set(existing_finance_item["relatedLots"]))
        else:
            new_finance["financingParty"]["id"] = eu_party["id"]
            existing_finance.append(new_finance)

    logger.info(f"Merged EU Funds Financing Identifier data for {len(eu_funds_financing_identifier_data['planning']['budget']['finance'])} finance items")