"""Converter for BT-11-Procedure-Buyer: Buyer legal type information.

This module handles mapping of buyer legal type codes from eForms to OCDS party
classifications using the eu-buyer-legal-type scheme.
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

# Mapping of buyer legal type codes to descriptions
BUYER_LEGAL_TYPE_CODES = {
    "body-pl": "Body governed by public law",
    "body-pl-cga": "Body governed by public law, controlled by a central government authority",
    "body-pl-la": "Body governed by public law, controlled by a local authority",
    "body-pl-ra": "Body governed by public law, controlled by a regional authority",
    "cga": "Central government authority",
    "def-cont": "Defence contractor",
    "eu-ins-bod-ag": "EU institution, body or agency",
    "eu-int-org": "European Institution/Agency or International Organisation",
    "grp-p-aut": "Group of public authorities",
    "int-org": "International organisation",
    "la": "Local authority",
    "org-sub": "Organisation awarding a contract subsidised by a contracting authority",
    "org-sub-cga": "Organisation awarding a contract subsidised by a central government authority",
    "org-sub-la": "Organisation awarding a contract subsidised by a local authority",
    "org-sub-ra": "Organisation awarding a contract subsidised by a regional authority",
    "pub-undert": "Public undertaking",
    "pub-undert-cga": "Public undertaking, controlled by a central government authority",
    "pub-undert-la": "Public undertaking, controlled by a local authority",
    "pub-undert-ra": "Public undertaking, controlled by a regional authority",
    "ra": "Regional authority",
    "rl-aut": "Regional or local authority",
    "spec-rights-entity": "Entity with special or exclusive rights",
}


def parse_buyer_legal_type(
    xml_content: str | bytes,
) -> dict[str, list[dict[str, Any]]] | None:
    """Parse buyer legal type information from XML and map to OCDS classifications.

    Gets the organization ID and buyer legal type code for each ContractingParty and
    maps them to OCDS party classifications using the eu-buyer-legal-type scheme.

    Args:
        xml_content: XML string or bytes to parse

    Returns:
        dict | None: Dictionary in format:
            {
                "parties": [
                    {
                        "id": str,  # Organization ID
                        "details": {
                            "classifications": [
                                {
                                    "scheme": "eu-buyer-legal-type",
                                    "id": str,  # Legal type code
                                    "description": str  # Human readable description
                                }
                            ]
                        }
                    }
                ]
            }
        Returns None if no buyer legal type data found

    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")
    root = etree.fromstring(xml_content)

    result = {"parties": []}
    contracting_parties = root.xpath("//cac:ContractingParty", namespaces=NAMESPACES)

    for party in contracting_parties:
        org_id = party.xpath(
            ".//cac:PartyIdentification/cbc:ID[@schemeName='organization']/text()",
            namespaces=NAMESPACES,
        )
        legal_type = party.xpath(
            ".//cac:ContractingPartyType/cbc:PartyTypeCode[@listName='buyer-legal-type']/text()",
            namespaces=NAMESPACES,
        )

        if org_id and legal_type:
            org_id = org_id[0]
            legal_type_code = legal_type[0]
            description = BUYER_LEGAL_TYPE_CODES.get(
                legal_type_code, "Unknown buyer legal type"
            )

            party_data = {
                "id": org_id,
                "details": {
                    "classifications": [
                        {
                            "scheme": "eu-buyer-legal-type",
                            "id": legal_type_code,
                            "description": description,
                        }
                    ],
                },
            }
            result["parties"].append(party_data)

    return result if result["parties"] else None


def merge_buyer_legal_type(
    release_json: dict, buyer_legal_type_data: dict[str, list[dict[str, Any]]] | None
) -> None:
    """Merge buyer legal type classifications into the OCDS release.

    Adds or updates party details.classifications with buyer legal type information
    using the eu-buyer-legal-type scheme.

    Args:
        release_json: Target release JSON to update
        buyer_legal_type_data: Party classification data in format:
            {
                "parties": [
                    {
                        "id": str,
                        "details": {
                            "classifications": [...]
                        }
                    }
                ]
            }

    Note:
        Updates release_json in-place

    """
    if not buyer_legal_type_data:
        logger.warning("No buyer Legal Type data to merge")
        return

    if "parties" not in release_json:
        release_json["parties"] = []

    for new_party in buyer_legal_type_data["parties"]:
        existing_party = next(
            (
                party
                for party in release_json["parties"]
                if party["id"] == new_party["id"]
            ),
            None,
        )
        if existing_party:
            if "details" not in existing_party:
                existing_party["details"] = {}
            if "classifications" not in existing_party["details"]:
                existing_party["details"]["classifications"] = []
            existing_party["details"]["classifications"].append(
                new_party["details"]["classifications"][0],
            )
        else:
            release_json["parties"].append(new_party)

    logger.info(
        "Merged buyer Legal Type data for %d parties",
        len(buyer_legal_type_data["parties"]),
    )
