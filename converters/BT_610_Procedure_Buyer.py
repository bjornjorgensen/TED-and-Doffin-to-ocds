# converters/BT_610_Procedure_Buyer.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)

COFOG_ACTIVITIES = [
    "gen-pub",
    "defence",
    "pub-os",
    "econ-aff",
    "env-pro",
    "hc-am",
    "health",
    "rcr",
    "education",
    "soc-pro",
]

COFOG_MAPPING = {
    "gen-pub": ("01", "General public services"),
    "defence": ("02", "Defence"),
    "pub-os": ("03", "Public order and safety"),
    "econ-aff": ("04", "Economic affairs"),
    "env-pro": ("05", "Environmental protection"),
    "hc-am": ("06", "Housing and community amenities"),
    "health": ("07", "Health"),
    "rcr": ("08", "Recreation, culture and religion"),
    "education": ("09", "Education"),
    "soc-pro": ("10", "Social protection"),
}

EU_MAIN_ACTIVITY_MAPPING = {
    "airport": "Airport-related activities",
    "defence": "Defence",
    "econ-aff": "Economic affairs",
    "education": "Education",
    "electricity": "Electricity-related activities",
    "env-pro": "Environmental protection",
    "gas-heat": "Production, transport or distribution of gas or heat",
    "gas-oil": "Extraction of gas or oil",
    "gen-pub": "General public services",
    "hc-am": "Housing and community amenities",
    "health": "Health",
    "port": "Port-related activities",
    "post": "Postal services",
    "pub-os": "Public order and safety",
    "rail": "Railway services",
    "rcr": "Recreation, culture and religion",
    "soc-pro": "Social protection",
    "solid-fuel": "Exploration or extraction of coal or other solid fuels",
    "urttb": "Urban railway, tramway, trolleybus or bus services",
    "water": "Water-related activities",
}


def parse_activity_entity(xml_content):
    """
    Parse the XML content to extract the main activity of the contracting entity.

    This function processes the BT-610-Procedure-Buyer business term, which represents
    the main activity of the contracting entity.

    Args:
        xml_content (str): The XML content to parse.

    Returns:
        dict: A dictionary containing the parsed activity entity data in the format:
              {
                  "parties": [
                      {
                          "id": "buyer_id",
                          "roles": ["buyer"],
                          "details": {
                              "classifications": [
                                  {
                                      "scheme": "scheme_name",
                                      "id": "activity_id",
                                      "description": "activity_description"
                                  }
                              ]
                          }
                      }
                  ]
              }
        None: If no relevant data is found.

    Raises:
        etree.XMLSyntaxError: If the input is not valid XML.
    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")
    root = etree.fromstring(xml_content)
    namespaces = {
        "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
        "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
        "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
        "efext": "http://data.europa.eu/p27/eforms-ubl-extensions/1",
        "efbc": "http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1",
    }

    result = {"parties": []}

    contracting_parties = root.xpath("//cac:ContractingParty", namespaces=namespaces)

    for party in contracting_parties:
        buyer_id = party.xpath(
            "cac:Party/cac:PartyIdentification/cbc:ID/text()", namespaces=namespaces
        )
        activity_code = party.xpath(
            "cac:ContractingActivity/cbc:ActivityTypeCode[@listName='entity-activity']/text()",
            namespaces=namespaces,
        )

        if buyer_id and activity_code:
            buyer_id = buyer_id[0]
            activity_code = activity_code[0]

            classification = {}
            if activity_code in COFOG_ACTIVITIES:
                classification["scheme"] = "COFOG"
                classification["id"] = COFOG_MAPPING[activity_code][0]
                classification["description"] = COFOG_MAPPING[activity_code][1]
            else:
                classification["scheme"] = "eu-main-activity"
                classification["id"] = activity_code
                classification["description"] = EU_MAIN_ACTIVITY_MAPPING.get(
                    activity_code, ""
                )

            party_data = {
                "id": buyer_id,
                "roles": ["buyer"],
                "details": {"classifications": [classification]},
            }
            result["parties"].append(party_data)

    return result if result["parties"] else None


def merge_activity_entity(release_json, activity_data):
    """
    Merge the parsed activity entity data into the main OCDS release JSON.

    This function updates the existing parties in the release JSON with the
    activity entity information. If a party doesn't exist, it adds a new party to the release.

    Args:
        release_json (dict): The main OCDS release JSON to be updated.
        activity_data (dict): The parsed activity entity data to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not activity_data:
        logger.warning("BT-610-Procedure-Buyer: No activity entity data to merge")
        return

    existing_parties = release_json.setdefault("parties", [])

    for new_party in activity_data["parties"]:
        existing_party = next(
            (party for party in existing_parties if party["id"] == new_party["id"]),
            None,
        )
        if existing_party:
            existing_party.setdefault("details", {}).setdefault(
                "classifications", []
            ).extend(new_party["details"]["classifications"])
            if "buyer" not in existing_party.get("roles", []):
                existing_party.setdefault("roles", []).append("buyer")
        else:
            existing_parties.append(new_party)

    logger.info(
        f"BT-610-Procedure-Buyer: Merged activity entity data for {len(activity_data['parties'])} parties"
    )
