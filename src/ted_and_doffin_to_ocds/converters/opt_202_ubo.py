# converters/OPT_202_ubo.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)


def parse_ubo_identifier(xml_content):
    """
    Parse the XML content to extract the Ultimate Beneficial Owner identifier.

    Args:
        xml_content (str): The XML content to parse.

    Returns:
        dict: A dictionary containing the parsed ubo data.
        None: If no relevant data is found.
    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")

    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")
    root = etree.fromstring(xml_content)
    namespaces = {
        "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
        "efext": "http://data.europa.eu/p27/eforms-ubl-extensions/1",
        "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
        "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
    }

    result = {"parties": []}

    organizations = root.xpath(
        "//efac:organizations/efac:organization",
        namespaces=namespaces,
    )

    for organization in organizations:
        org_id = organization.xpath(
            "efac:company/cac:partyIdentification/cbc:ID[@schemeName='organization']/text()",
            namespaces=namespaces,
        )
        ubos = root.xpath(
            "//efac:organizations/efac:UltimateBeneficialOwner",
            namespaces=namespaces,
        )

        if org_id and ubos:
            party = {"id": org_id[0], "beneficialOwners": []}

            for ubo in ubos:
                ubo_id = ubo.xpath(
                    "cbc:ID[@schemeName='ubo']/text()",
                    namespaces=namespaces,
                )
                if ubo_id:
                    party["beneficialOwners"].append({"id": ubo_id[0]})

            if party["beneficialOwners"]:
                result["parties"].append(party)

    return result if result["parties"] else None


def merge_ubo_identifier(release_json, ubo_data):
    """
    Merge the parsed ubo data into the main OCDS release JSON.

    Args:
        release_json (dict): The main OCDS release JSON to be updated.
        ubo_data (dict): The parsed ubo data to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not ubo_data:
        logger.warning("No ubo data to merge")
        return

    existing_parties = release_json.setdefault("parties", [])

    for new_party in ubo_data["parties"]:
        existing_party = next(
            (party for party in existing_parties if party["id"] == new_party["id"]),
            None,
        )
        if existing_party:
            existing_ubos = {
                ubo["id"] for ubo in existing_party.get("beneficialOwners", [])
            }
            for new_ubo in new_party["beneficialOwners"]:
                if new_ubo["id"] not in existing_ubos:
                    existing_party.setdefault("beneficialOwners", []).append(new_ubo)
                    existing_ubos.add(new_ubo["id"])
        else:
            existing_parties.append(new_party)

    logger.info(f"Merged ubo data for {len(ubo_data['parties'])} parties")
