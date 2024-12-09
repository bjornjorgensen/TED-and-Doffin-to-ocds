# converters/opt_301_part_docprovider.py

import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)


def parse_document_provider_part(xml_content: str | bytes) -> dict[str, Any] | None:
    """Parse document provider details from procurement project parts.

    Identifies organizations that serve as document providers.
    Adds processContactPoint role to identified organizations.

    Args:
        xml_content: XML content containing part data

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

    xpath = "/*/cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']/cac:TenderingTerms/cac:DocumentProviderParty/cac:PartyIdentification/cbc:ID[@schemeName='touchpoint']"
    document_providers = root.xpath(xpath, namespaces=namespaces)

    if not document_providers:
        logger.info("No Document Provider Technical Identifier found.")
        return None

    result = {"parties": []}
    for provider in document_providers:
        result["parties"].append(
            {"id": provider.text, "roles": ["processContactPoint"]}
        )

    return result


def merge_document_provider_part(
    release_json: dict[str, Any], document_provider_data: dict[str, Any] | None
) -> None:
    """Merge document provider data from parts into the release JSON.

    Args:
        release_json: Target release JSON to update
        document_provider_data: Provider data containing organizations and roles

    Effects:
        Updates the parties section of release_json with processContactPoint roles,
        merging with existing party roles where applicable

    """
    if not document_provider_data:
        logger.info("No Document Provider data to merge.")
        return

    parties = release_json.setdefault("parties", [])

    for new_party in document_provider_data["parties"]:
        existing_party = next(
            (party for party in parties if party["id"] == new_party["id"]), None
        )
        if existing_party:
            if "processContactPoint" not in existing_party["roles"]:
                existing_party["roles"].append("processContactPoint")
        else:
            parties.append(new_party)

    logger.info(
        "Merged Document Provider data for %d parties.",
        len(document_provider_data["parties"]),
    )
