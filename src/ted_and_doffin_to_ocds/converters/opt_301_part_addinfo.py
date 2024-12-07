# converters/opt_301_part_addinfo.py

import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)


def parse_additional_info_provider_part(
    xml_content: str | bytes,
) -> dict[str, Any] | None:
    """
    Parse additional information provider details from parts.

    Identifies organizations that serve as information contact points for parts.
    Adds processContactPoint role to identified organizations.

    Args:
        xml_content: XML content containing procurement part data

    Returns:
        Optional[Dict]: Dictionary containing parties with roles, or None if no data.
        Example structure:
        {
            "parties": [
                {
                    "id": "org_id",
                    "roles": ["processContactPoint"]
                }
            ]
        }
    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")
    root = etree.fromstring(xml_content)
    namespaces = {
        "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    }

    xpath = "/*/cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']/cac:TenderingTerms/cac:AdditionalInformationParty/cac:PartyIdentification/cbc:ID[@schemeName='touchpoint']"
    additional_info_providers = root.xpath(xpath, namespaces=namespaces)

    if not additional_info_providers:
        logger.info("No Additional Info Provider Technical Identifier found.")
        return None

    result = {"parties": []}
    for provider in additional_info_providers:
        result["parties"].append(
            {"id": provider.text, "roles": ["processContactPoint"]}
        )

    return result


def merge_additional_info_provider_part(
    release_json: dict[str, Any], additional_info_data: dict[str, Any] | None
) -> None:
    """
    Merge additional information provider data from parts into the release JSON.

    Args:
        release_json: Target release JSON to update
        additional_info_data: Additional info provider data containing organizations

    Effects:
        Updates the parties section of release_json with processContactPoint roles,
        merging with existing party roles where applicable
    """
    if not additional_info_data:
        logger.info("No Additional Info Provider data to merge.")
        return

    parties = release_json.setdefault("parties", [])

    for new_party in additional_info_data["parties"]:
        existing_party = next(
            (party for party in parties if party["id"] == new_party["id"]), None
        )
        if existing_party:
            if "processContactPoint" not in existing_party["roles"]:
                existing_party["roles"].append("processContactPoint")
        else:
            parties.append(new_party)

    logger.info(
        "Merged Additional Info Provider data for %d parties.",
        len(additional_info_data["parties"]),
    )
