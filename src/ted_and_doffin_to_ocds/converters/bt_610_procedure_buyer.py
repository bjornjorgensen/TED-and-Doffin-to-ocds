# converters/bt_610_procedure_buyer.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)

# COFOG codes and descriptions
COFOG_MAPPING = {
    "defence": ("02", "Defence"),
    "econ-aff": ("04", "Economic affairs"),
    "education": ("09", "Education"),
    "env-pro": ("05", "Environmental protection"),
    "gen-pub": ("01", "General public services"),
    "hc-am": ("06", "Housing and community amenities"),
    "health": ("07", "Health"),
    "pub-os": ("03", "Public order and safety"),
    "rcr": ("08", "Recreation, culture and religion"),
    "soc-pro": ("10", "Social protection"),
}

# Authority activity descriptions for non-COFOG activities
AUTHORITY_TABLE = {
    "gas-oil": "Activities related to the exploitation of a geographical area for the purpose of extracting oil or gas.",
    "port": "Activities related to the exploitation of a geographical area for the purpose of the provision of maritime or inland ports or other terminal facilities to carriers by sea or inland waterway.",
    "water": "Activities related to: (a) the provision or operation of fixed networks intended to provide a service to the public in connection with the production, transport or distribution of drinking water; (b) the supply of drinking water to such networks; (c) hydraulic engineering projects, irrigation or land drainage, provided that the volume of water to be used for the supply of drinking water represents more than 20 % of the total volume of water made available by such projects or irrigation or drainage installations; (d) the disposal or treatment of sewage.",
    "airport": "Activities related to the exploitation of a geographical area for the purpose of the provision of airports or other terminal facilities to carriers by air.",
    "post": "Activities related to the exploitation of a geographical area for the purpose of the provision of maritime or inland ports or other terminal facilities to carriers by sea or inland waterway.",
    "electricity": "Activities related to: (a) the provision or operation of fixed networks intended to provide a service to the public in connection with the production, transport or distribution of electricity; (b) the supply of electricity to such networks.",
    "gas-heat": "Activities related to: (a) the provision or operation of fixed networks intended to provide a service to the public in connection with the production, transport or distribution of gas or heat; (b) the supply of gas or heat to such networks.",
    "solid-fuel": "Activities related to the exploitation of a geographical area for the purpose of exploring for, or extracting, coal or other solid fuels.",
    "urttb": "Activities relating to the provision or operation of networks providing a service to the public in the field of transport by railway, automated systems, tramway, trolley bus, bus or cable.",
    "rail": "Activities related to the provision or operation of networks providing a service to the public in the field of transport by railway.",
}


def parse_activity_entity(xml_content):
    """
    Parse the XML content to extract the main activity of the contracting entity.

    This function processes the BT-610-procedure-buyer business term, which represents
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
            "cac:Party/cac:PartyIdentification/cbc:ID/text()",
            namespaces=namespaces,
        )
        activity_code = party.xpath(
            "cac:ContractingActivity/cbc:ActivityTypeCode[@listName='entity-activity']/text()",
            namespaces=namespaces,
        )

        if buyer_id and activity_code:
            buyer_id = buyer_id[0]
            activity_code = activity_code[0]

            classification = {}
            if activity_code in COFOG_MAPPING:
                # Handle COFOG classification
                classification.update(
                    {
                        "scheme": "COFOG",
                        "id": COFOG_MAPPING[activity_code][0],
                        "description": COFOG_MAPPING[activity_code][1],
                    }
                )
            elif activity_code in AUTHORITY_TABLE:
                # Handle non-COFOG classification
                classification.update(
                    {
                        "scheme": "eu-main-activity",
                        "id": activity_code,
                        "description": AUTHORITY_TABLE[activity_code],
                    }
                )
            else:
                logger.warning("Unknown activity code: %s", activity_code)
                continue

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
        logger.warning("BT-610-procedure-buyer: No activity entity data to merge")
        return

    existing_parties = release_json.setdefault("parties", [])

    for new_party in activity_data["parties"]:
        existing_party = next(
            (party for party in existing_parties if party["id"] == new_party["id"]),
            None,
        )
        if existing_party:
            existing_party.setdefault("details", {}).setdefault(
                "classifications",
                [],
            ).extend(new_party["details"]["classifications"])
            if "buyer" not in existing_party.get("roles", []):
                existing_party.setdefault("roles", []).append("buyer")
        else:
            existing_parties.append(new_party)

    logger.info(
        "BT-610-procedure-buyer: Merged activity entity data for %d parties",
        len(activity_data["parties"]),
    )
