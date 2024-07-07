# converters/BT_60_Lot.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)

def parse_eu_funds(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
        'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1'
    }

    eu_funded = root.xpath("//efac:Funding/cbc:FundingProgramCode[@listName='eu-funded']/text()", namespaces=namespaces)

    if eu_funded and eu_funded[0].lower() == 'eu-funds':
        return {
            "parties": [
                {
                    "name": "European Union",
                    "roles": ["funder"]
                }
            ]
        }
    return None

def merge_eu_funds(release_json, eu_funds_data):
    if not eu_funds_data:
        logger.warning("No EU Funds data to merge")
        return

    existing_parties = release_json.setdefault("parties", [])
    eu_party = next((party for party in existing_parties if party.get("name") == "European Union"), None)

    if eu_party:
        if "funder" not in eu_party.get("roles", []):
            eu_party.setdefault("roles", []).append("funder")
    else:
        new_party = eu_funds_data["parties"][0]
        new_party["id"] = str(len(existing_parties) + 1)
        existing_parties.append(new_party)

    logger.info("Merged EU Funds data")