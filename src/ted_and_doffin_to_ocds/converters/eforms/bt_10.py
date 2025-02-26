"""BT-10 Authority Activity converter.

Maps contracting authority main activities to OCDS party classifications.
Handles both COFOG and EU-specific activity classifications.
"""

import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)

NAMESPACES = {
    "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
    "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
    "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
    "efext": "http://data.europa.eu/p27/eforms-ubl-extensions/1",
    "efbc": "http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1",
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

# COFOG codes and descriptions per UN Classifications standard
COFOG_TABLE = {
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


def parse_authority_activity(xml_content: str | bytes) -> dict[str, Any] | None:
    """Parse the authority activity (BT-10) from XML content.

    Extracts authority activity codes for each contracting party and maps them
    to OCDS party classifications using either COFOG or eu-main-activity schemes.

    Args:
        xml_content: XML string or bytes to parse

    Returns:
        Dictionary containing party classifications like:
        {
            "parties": [{
                "id": "<org-id>",
                "details": {
                    "classifications": [{
                        "scheme": "<COFOG|eu-main-activity>",
                        "id": "<activity-code>",
                        "description": "<activity-description>"
                    }]
                }
            }]
        }
        or None if no authority activity found
    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")
    root = etree.fromstring(xml_content)

    # Check if the relevant XPath exists
    relevant_xpath = "//cac:ContractingParty/cac:ContractingActivity/cbc:ActivityTypeCode[@listName='authority-activity']"
    if not root.xpath(relevant_xpath, namespaces=NAMESPACES):
        logger.info(
            "No authority activity data found. Skipping parse_authority_activity."
        )
        return None

    result = {"parties": []}

    # Process each contracting party
    contracting_parties = root.xpath("//cac:ContractingParty", namespaces=NAMESPACES)

    for party in contracting_parties:
        organization_id = party.xpath(
            "cac:Party/cac:PartyIdentification/cbc:ID[@schemeName='organization']/text()",
            namespaces=NAMESPACES,
        )
        activity_code = party.xpath(
            "cac:ContractingActivity/cbc:ActivityTypeCode[@listName='authority-activity']/text()",
            namespaces=NAMESPACES,
        )

        if organization_id and activity_code:
            code = activity_code[0]
            classification = None

            # Handle COFOG classifications
            if code in COFOG_TABLE:
                cofog_id, description = COFOG_TABLE[code]
                classification = {
                    "scheme": "COFOG",
                    "id": cofog_id,
                    "description": description,
                }
            # Handle non-COFOG classifications
            elif code in AUTHORITY_TABLE:
                classification = {
                    "scheme": "eu-main-activity",
                    "id": code,
                    "description": AUTHORITY_TABLE[code],
                }

            if classification:
                party_data = {
                    "id": organization_id[0],
                    "details": {"classifications": [classification]},
                }
                result["parties"].append(party_data)

    return result if result["parties"] else None


def merge_authority_activity(
    release_json: dict[str, Any], authority_activity_data: dict[str, Any] | None
) -> None:
    """Merge authority activity data into the release JSON.

    Updates party details with authority activity classifications.
    Preserves existing classifications while adding new ones.

    Args:
        release_json: The target release JSON to update
        authority_activity_data: The authority activity data to merge

    """
    if not authority_activity_data:
        logger.info("No authority activity data to merge")
        return

    existing_parties = release_json.setdefault("parties", [])

    for new_party in authority_activity_data["parties"]:
        existing_party = next(
            (party for party in existing_parties if party["id"] == new_party["id"]),
            None,
        )

        if existing_party:
            existing_details = existing_party.setdefault("details", {})
            existing_classifications = existing_details.setdefault(
                "classifications", []
            )
            new_classifications = new_party["details"]["classifications"]

            for new_classification in new_classifications:
                if not any(
                    cls["scheme"] == new_classification["scheme"]
                    and cls["id"] == new_classification["id"]
                    for cls in existing_classifications
                ):
                    existing_classifications.append(new_classification)
        else:
            existing_parties.append(new_party)

    logger.info(
        "Merged authority activity data for %d parties",
        len(authority_activity_data["parties"]),
    )
