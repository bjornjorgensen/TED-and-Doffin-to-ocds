# converters/BT_60_Lot.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)

def parse_eu_funds(xml_content):
    """
    Parse the XML content to check if the procurement is financed by EU funds.

    This function processes the BT-60-Lot business term, which indicates whether
    the procurement is at least partially financed by Union funds.

    Args:
        xml_content (str): The XML content to parse.

    Returns:
        dict: A dictionary containing the EU funder information if EU funds are used:
              {
                  "parties": [
                      {
                          "name": "European Union",
                          "roles": ["funder"]
                      }
                  ]
              }
        None: If no EU funds are indicated.

    Raises:
        etree.XMLSyntaxError: If the input is not valid XML.
    """
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
        'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1'
    }

    eu_funded = root.xpath("//efac:Funding/cbc:FundingProgramCode[@listName='eu-funded' and text()='eu-funds']", namespaces=namespaces)

    if eu_funded:
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
    """
    Merge the parsed EU funds data into the main OCDS release JSON.

    This function adds or updates the European Union as a funder in the parties array.

    Args:
        release_json (dict): The main OCDS release JSON to be updated.
        eu_funds_data (dict): The parsed EU funds data to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not eu_funds_data:
        logger.info("BT-60-Lot: No EU funds data to merge")
        return

    parties = release_json.setdefault("parties", [])
    eu_party = next((party for party in parties if party.get("name") == "European Union"), None)

    if eu_party:
        if "funder" not in eu_party.get("roles", []):
            eu_party.setdefault("roles", []).append("funder")
    else:
        new_eu_party = eu_funds_data["parties"][0]
        new_eu_party["id"] = str(len(parties) + 1)  # Assign a new ID
        parties.append(new_eu_party)

    logger.info("BT-60-Lot: Merged EU funds data")