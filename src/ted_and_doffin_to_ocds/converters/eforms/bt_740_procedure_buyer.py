import logging

from lxml import etree

logger = logging.getLogger(__name__)

NAMESPACES = {
    "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
    "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
    "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
}

# Mapping for BT-740: Buyer contracting entity status
BUYER_TYPE_MAPPING = {
    "cont-ent": "Contracting Entity",
    "not-cont-ent": "Not Contracting Entity",
}


def parse_buyer_contracting_type(xml_content: str | bytes) -> dict | None:
    """Parse BT-740: Buyer contracting entity status.

    Extracts whether buyers are contracting entities and maps their classification
    according to the buyer contracting type scheme.

    Args:
        xml_content: XML content to parse, either as string or bytes

    Returns:
        Optional[Dict]: Parsed data in format:
            {
                "parties": [
                    {
                        "id": str,
                        "details": {
                            "classifications": [
                                {
                                    "scheme": "eu-buyer-contracting-type",
                                    "id": str,
                                    "description": str
                                }
                            ]
                        },
                        "roles": ["buyer"]
                    }
                ]
            }
        Returns None if no relevant data found or on error

    """
    try:
        if isinstance(xml_content, str):
            xml_content = xml_content.encode("utf-8")
        root = etree.fromstring(xml_content)
        result = {"parties": []}

        # Find ContractingPartyType elements as per BT-740 XPath:
        # /*/cac:ContractingParty/cac:ContractingPartyType/cbc:PartyTypeCode[@listName='buyer-contracting-type']
        contracting_parties = root.xpath(
            "/*/cac:ContractingParty/cac:ContractingPartyType", namespaces=NAMESPACES
        )

        for party in contracting_parties:
            org_id = party.xpath(
                "cac:Party/cac:PartyIdentification/cbc:ID/text()", namespaces=NAMESPACES
            )
            type_code = party.xpath(
                "cbc:PartyTypeCode[@listName='buyer-contracting-type']/text()",
                namespaces=NAMESPACES,
            )

            if org_id and type_code:
                code = type_code[0]
                description = BUYER_TYPE_MAPPING.get(code, "Unknown")
                logger.info(
                    "Found buyer contracting type %s for organization %s",
                    description,
                    org_id[0],
                )
                party_data = {
                    "id": org_id[0],
                    "details": {
                        "classifications": [
                            {
                                "scheme": "eu-buyer-contracting-type",
                                "id": code,
                                "description": description,
                            }
                        ]
                    },
                    "roles": ["buyer"],
                }
                result["parties"].append(party_data)

        return result if result["parties"] else None

    except etree.XMLSyntaxError:
        logger.exception("Failed to parse XML content")
        raise
    except Exception:
        logger.exception("Error processing buyer contracting type")
        return None


def merge_buyer_contracting_type(
    release_json: dict, buyer_type_data: dict | None
) -> None:
    """Merge buyer contracting type data into the release JSON.

    Updates or adds buyer classifications and roles.

    Args:
        release_json: Main OCDS release JSON to update
        buyer_type_data: Buyer contracting type data to merge, can be None

    Note:
        - Updates release_json in-place
        - Creates parties array if needed
        - Updates existing parties' details.classifications
        - Ensures buyer role is present

    """
    if not buyer_type_data:
        logger.warning("No buyer contracting type data to merge")
        return

    parties = release_json.setdefault("parties", [])

    for new_party in buyer_type_data["parties"]:
        existing_party = next((p for p in parties if p["id"] == new_party["id"]), None)
        if existing_party:
            details = existing_party.setdefault("details", {})
            classifications = details.setdefault("classifications", [])

            # Update or add classification
            new_class = new_party["details"]["classifications"][0]
            existing_class = next(
                (c for c in classifications if c["scheme"] == new_class["scheme"]), None
            )
            if existing_class:
                existing_class.update(new_class)
            else:
                classifications.append(new_class)

            # Ensure buyer role
            roles = existing_party.setdefault("roles", [])
            if "buyer" not in roles:
                roles.append("buyer")
        else:
            parties.append(new_party)

    logger.info(
        "Merged buyer contracting type data for %d parties",
        len(buyer_type_data["parties"]),
    )
