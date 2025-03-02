import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)


def parse_buyer_technical_identifier(
    xml_content: str | bytes,
) -> dict[str, Any] | None:
    """Parse buyer technical identifiers from contracting party information.

    Creates party entries with buyer role and links them through buyer reference.

    Args:
        xml_content: XML content containing buyer data

    Returns:
        Optional[Dict]: Dictionary containing parties and buyer reference, or None if no data.
        Example structure:
        {
            "parties": [
                {
                    "id": "org_id",
                    "roles": ["buyer"]
                }
            ],
            "buyer": {
                "id": "org_id"
            }
        }

    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")
    root = etree.fromstring(xml_content)
    namespaces = {
        "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    }

    result = {"parties": []}

    xpath_query = "/*/cac:ContractingParty/cac:Party/cac:PartyIdentification/cbc:ID"
    buyer_id_elements = root.xpath(xpath_query, namespaces=namespaces)

    if buyer_id_elements:
        # Take first buyer as main buyer
        buyer_id = buyer_id_elements[0].text
        result["parties"].append({"id": buyer_id, "roles": ["buyer"]})
        result["buyer"] = {"id": buyer_id}

        # Add any additional buyers as parties only
        for id_element in buyer_id_elements[1:]:
            result["parties"].append({"id": id_element.text, "roles": ["buyer"]})

    return result if result["parties"] else None


def merge_buyer_technical_identifier(
    release_json: dict[str, Any], buyer_data: dict[str, Any] | None
) -> None:
    """Merge buyer technical identifier data into the release JSON.

    Args:
        release_json: Target release JSON to update
        buyer_data: Buyer data containing identifiers

    Effects:
        - Updates parties section with buyer roles
        - Sets single buyer reference

    """
    if not buyer_data:
        return

    parties = release_json.setdefault("parties", [])

    for new_party in buyer_data["parties"]:
        existing_party = next(
            (party for party in parties if party["id"] == new_party["id"]), None
        )
        if existing_party:
            if "buyer" not in existing_party.get("roles", []):
                existing_party.setdefault("roles", []).append("buyer")
        else:
            parties.append(new_party)

    # Update buyer reference - only set if not already present
    if buyer_data and "buyer" in buyer_data and not release_json.get("buyer"):
        release_json["buyer"] = buyer_data["buyer"]
        logger.info("Set buyer reference to %s", buyer_data["buyer"]["id"])
