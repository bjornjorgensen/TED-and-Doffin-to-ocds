# converters/bt_739_ubo.py

import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)

NAMESPACES = {
    "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
    "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
    "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
    "efext": "http://data.europa.eu/p27/eforms-ubl-extensions/1",
}


def parse_ubo_fax(xml_content: str | bytes) -> dict[str, list[dict[str, Any]]] | None:
    """
    Parse Ultimate Beneficial Owner fax information from XML.

    Args:
        xml_content: XML content to parse

    Returns:
        Dictionary containing parties with UBO fax info, or None if not found
    """
    try:
        if isinstance(xml_content, str):
            xml_content = xml_content.encode("utf-8")

        root = etree.fromstring(xml_content)

        # Find organizations
        organizations = root.xpath(
            "//efext:EformsExtension/efac:Organizations/efac:Organization",
            namespaces=NAMESPACES,
        )

        if not organizations:
            return None

        parties = []
        for org in organizations:
            # Get organization ID
            org_id = org.xpath(
                ".//cac:PartyIdentification/cbc:ID[@schemeName='organization']/text()",
                namespaces=NAMESPACES,
            )

            if not org_id:
                continue

            # Get UBO info
            ubos = []
            ubo_elements = org.xpath(
                ".//efac:UltimateBeneficialOwner", namespaces=NAMESPACES
            )

            for ubo in ubo_elements:
                ubo_id = ubo.xpath(
                    "cbc:ID[@schemeName='ubo']/text()", namespaces=NAMESPACES
                )
                fax = ubo.xpath("cac:Contact/cbc:Telefax/text()", namespaces=NAMESPACES)

                if ubo_id and fax:
                    ubos.append({"id": ubo_id[0], "faxNumber": fax[0]})

            if ubos:
                parties.append({"id": org_id[0], "beneficialOwners": ubos})

    except etree.XMLSyntaxError:
        logger.exception("Failed to parse XML content")
        return None
    else:
        if parties:
            return {"parties": parties}
        return None


def merge_ubo_fax(
    release_json: dict[str, Any], ubo_data: dict[str, list[dict[str, Any]]] | None
) -> None:
    """
    Merge UBO fax data into the release JSON.

    Args:
        release_json: The target release JSON to update
        ubo_data: The UBO fax data to merge
    """
    if not ubo_data or "parties" not in ubo_data:
        return

    # Get or create parties list
    existing_parties = release_json.setdefault("parties", [])

    # Merge UBO data
    for new_party in ubo_data["parties"]:
        existing_party = next(
            (p for p in existing_parties if p["id"] == new_party["id"]), None
        )

        if existing_party:
            # Get or create beneficialOwners list
            existing_ubos = existing_party.setdefault("beneficialOwners", [])

            # Update or add UBO info
            for new_ubo in new_party["beneficialOwners"]:
                existing_ubo = next(
                    (u for u in existing_ubos if u["id"] == new_ubo["id"]), None
                )

                if existing_ubo:
                    existing_ubo["faxNumber"] = new_ubo["faxNumber"]
                else:
                    existing_ubos.append(new_ubo)
        else:
            existing_parties.append(new_party)
