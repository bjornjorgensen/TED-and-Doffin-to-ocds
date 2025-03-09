# converters/bt_16_organization_company.py

import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)


def parse_organization_part_name(xml_content: str | bytes) -> dict[str, Any] | None:
    """Parse organization part names from XML content.

    Handles eForms BT-16 (Organisation Part Name) by extracting department names
    and appending them to organization names with " - " separator.

    Args:
        xml_content (Union[str, bytes]): The XML content to parse, either as string or bytes

    Returns:
        Optional[Dict[str, Any]]: Dictionary containing organization data with combined names,
                                 or None if no valid data is found

    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")
    root = etree.fromstring(xml_content)
    namespaces = {
        "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
        "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
        "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
        "efext": "http://data.europa.eu/p27/eforms-ubl-extensions/1",
    }

    result = {"parties": []}

    organizations = root.xpath(
        "//efac:Organizations/efac:Organization", namespaces=namespaces
    )
    for org in organizations:
        org_id = org.xpath(
            "efac:Company/cac:PartyIdentification/cbc:ID[@schemeName='organization']/text()",
            namespaces=namespaces,
        )
        org_name = org.xpath(
            "efac:Company/cac:PartyName/cbc:Name/text()", namespaces=namespaces
        )
        # Extract BT-16 Organization Part Name (department)
        part_name = org.xpath(
            "efac:Company/cac:PostalAddress/cbc:Department/text()",
            namespaces=namespaces,
        )

        if org_id and org_name:
            party = {"id": org_id[0], "name": org_name[0]}
            if part_name:
                # Implement BT-16 guidance: append department name with " - " separator
                party["name"] += f" - {part_name[0]}"
            result["parties"].append(party)

    return result if result["parties"] else None


def merge_organization_part_name(
    release_json: dict[str, Any], organization_part_name_data: dict[str, Any] | None
) -> None:
    """Merge organization part names into the release JSON.

    Updates organization names with their part names (BT-16) in the OCDS release.

    Args:
        release_json (Dict[str, Any]): The release JSON to update
        organization_part_name_data (Optional[Dict[str, Any]]): Organization data with combined names to merge

    """
    if not organization_part_name_data:
        logger.info("No organization part name data to merge")
        return

    existing_parties = release_json.setdefault("parties", [])

    for new_party in organization_part_name_data["parties"]:
        existing_party = next(
            (party for party in existing_parties if party["id"] == new_party["id"]),
            None,
        )
        if existing_party:
            existing_party["name"] = new_party["name"]
        else:
            existing_parties.append(new_party)

    logger.info(
        "Merged organization part name data for %d parties",
        len(organization_part_name_data["parties"]),
    )
