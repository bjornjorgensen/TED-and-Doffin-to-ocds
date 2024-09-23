# converters/BT_10.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)


def parse_contract_xml(xml_content):
    """
    Parse the XML content to extract contract information related to BT-10.

    Args:
        xml_content (str or bytes): The XML content to parse.

    Returns:
        dict: A dictionary containing the parsed contract information.
    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")
    root = etree.fromstring(xml_content)
    parties = []
    authority_table = {
        "airport": ("COFOG", "Airport-related activities", "04.7"),
        "defence": ("COFOG", "Defence", "02"),
        "econ-aff": ("COFOG", "Economic affairs", "04"),
        "education": ("COFOG", "Education", "09"),
        "electricity": ("COFOG", "Electricity-related activities", "04.3"),
        "env-pro": ("COFOG", "Environmental protection", "05"),
        "gas-heat": (
            "COFOG",
            "Production, transport or distribution of gas or heat",
            "04.3",
        ),
        "gas-oil": ("COFOG", "Extraction of gas or oil", "04.4"),
        "gen-pub": ("COFOG", "General public services", "01"),
        "hc-am": ("COFOG", "Housing and community amenities", "06"),
        "health": ("COFOG", "Health", "07"),
        "port": ("COFOG", "Port-related activities", "04.5"),
        "post": ("COFOG", "Postal services", "04.6"),
        "pub-os": ("COFOG", "Public order and safety", "03"),
        "rail": ("COFOG", "Railway services", "04.5"),
        "rcr": ("COFOG", "Recreation, culture and religion", "08"),
        "soc-pro": ("COFOG", "Social protection", "10"),
        "solid-fuel": (
            "COFOG",
            "Exploration or extraction of coal or other solid fuels",
            "04.4",
        ),
        "urttb": (
            "COFOG",
            "Urban railway, tramway, trolleybus or bus services",
            "04.5",
        ),
        "water": ("COFOG", "Water-related activities", "06.3"),
    }

    namespaces = {
        "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
        "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
        "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
        "efext": "http://data.europa.eu/p27/eforms-ubl-extensions/1",
        "efbc": "http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1",
    }

    contracting_parties = root.xpath("//cac:ContractingParty", namespaces=namespaces)

    for contracting_party in contracting_parties:
        party_id_elements = contracting_party.xpath(
            ".//cac:PartyIdentification/cbc:ID", namespaces=namespaces,
        )
        if not party_id_elements:
            logger.warning("Skipping contracting party without ID")
            continue

        party_id = party_id_elements[0].text

        activity_type_code_elements = contracting_party.xpath(
            ".//cbc:ActivityTypeCode[@listName='authority-activity']",
            namespaces=namespaces,
        )
        if not activity_type_code_elements:
            logger.warning(
                f"Skipping contracting party {party_id} without activity type code",
            )
            continue

        activity_type_code = activity_type_code_elements[0].text

        organization = next((org for org in parties if org["id"] == party_id), None)
        if not organization:
            organization = {
                "id": party_id,
                "roles": ["buyer"],
                "details": {"classifications": []},
            }
            parties.append(organization)

        if activity_type_code in authority_table:
            scheme, description, cofog_id = authority_table[activity_type_code]
            classification = {
                "scheme": scheme,
                "id": cofog_id,
                "description": description,
            }
        else:
            classification = {
                "scheme": "eu-main-activity",
                "id": activity_type_code,
                "description": activity_type_code,
            }

        organization["details"]["classifications"].append(classification)

    logger.info(f"Parsed {len(parties)} parties with BT-10 information")
    return {"parties": parties}


def merge_contract_info(release_json, contract_info):
    """
    Merge the parsed contract information into the main OCDS release JSON.

    Args:
        release_json (dict): The main OCDS release JSON to be updated.
        contract_info (dict): The parsed contract information to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not contract_info or not contract_info.get("parties"):
        logger.warning("No contract information to merge")
        return

    for new_party in contract_info["parties"]:
        existing_party = next(
            (
                party
                for party in release_json.get("parties", [])
                if party["id"] == new_party["id"]
            ),
            None,
        )
        if existing_party:
            if "details" not in existing_party:
                existing_party["details"] = {"classifications": []}
            elif "classifications" not in existing_party["details"]:
                existing_party["details"]["classifications"] = []
            existing_party["details"]["classifications"].extend(
                new_party["details"]["classifications"],
            )
        else:
            release_json.setdefault("parties", []).append(new_party)

    logger.info(f"Merged BT-10 information for {len(contract_info['parties'])} parties")
