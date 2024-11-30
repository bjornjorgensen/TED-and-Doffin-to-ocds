# converters/bt_508_procedure_buyer.py

import logging

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


def parse_buyer_profile_url(xml_content: str | bytes) -> dict[str, list[dict]] | None:
    """
    Parse the buyer profile URL from contracting party information.

    Args:
        xml_content: XML content to parse

    Returns:
        Dictionary containing parties data or None if no valid data found
    """
    try:
        if isinstance(xml_content, str):
            xml_content = xml_content.encode("utf-8")

        root = etree.fromstring(xml_content)

        contracting_parties = root.xpath(
            "//cac:ContractingParty", namespaces=NAMESPACES
        )
        if not contracting_parties:
            logger.debug("No contracting parties found")
            return None

        result = {"parties": []}

        for party in contracting_parties:
            buyer_profile = party.xpath(
                "cbc:BuyerProfileURI/text()", namespaces=NAMESPACES
            )
            party_id = party.xpath(
                "cac:Party/cac:PartyIdentification/cbc:ID/text()", namespaces=NAMESPACES
            )

            if buyer_profile and party_id:
                result["parties"].append(
                    {
                        "id": party_id[0],
                        "details": {"buyerProfile": buyer_profile[0]},
                        "roles": ["buyer"],
                    }
                )
                logger.info(
                    "Found buyer profile for party %s: %s",
                    party_id[0],
                    buyer_profile[0],
                )

        return result if result["parties"] else None

    except etree.XMLSyntaxError:
        logger.exception("Failed to parse XML content")
        return None
    except Exception:
        logger.exception("Error processing buyer profile")
        return None


def merge_buyer_profile_url(
    release_json: dict, buyer_profile_data: dict | None
) -> None:
    """
    Merge buyer profile URL data into release JSON.

    Args:
        release_json: Target release JSON to update
        buyer_profile_data: Buyer profile data to merge
    """
    if not buyer_profile_data or not buyer_profile_data.get("parties"):
        logger.debug("No buyer profile data to merge")
        return

    existing_parties = release_json.setdefault("parties", [])

    for new_party in buyer_profile_data["parties"]:
        # Find existing party by ID
        existing_party = next(
            (p for p in existing_parties if p["id"] == new_party["id"]), None
        )

        if existing_party:
            # Update existing party
            existing_party.setdefault("details", {})["buyerProfile"] = new_party[
                "details"
            ]["buyerProfile"]
            if "buyer" not in existing_party.get("roles", []):
                existing_party.setdefault("roles", []).append("buyer")
            logger.info("Updated buyer profile for existing party: %s", new_party["id"])
        else:
            # Add new party
            existing_parties.append(new_party)
            logger.info("Added new party with buyer profile: %s", new_party["id"])
