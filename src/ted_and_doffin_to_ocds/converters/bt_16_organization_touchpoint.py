# converters/bt_16_organization_touchpoint.py

import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)


def parse_organization_touchpoint_part_name(
    xml_content: str | bytes,
) -> dict[str, Any] | None:
    """Parse organization touchpoint part names from XML content.

    Args:
        xml_content (Union[str, bytes]): The XML content to parse, either as string or bytes

    Returns:
        Optional[Dict[str, Any]]: Dictionary containing organization data with combined names and identifiers,
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
        touchpoint = org.xpath("efac:TouchPoint", namespaces=namespaces)
        if touchpoint:
            touchpoint = touchpoint[0]
            touchpoint_id = touchpoint.xpath(
                "cac:PartyIdentification/cbc:ID[@schemeName='touchpoint']/text()",
                namespaces=namespaces,
            )
            org_name = touchpoint.xpath(
                "cac:PartyName/cbc:Name/text()", namespaces=namespaces
            )
            part_name = touchpoint.xpath(
                "cac:PostalAddress/cbc:Department/text()", namespaces=namespaces
            )
            company_id = org.xpath(
                "efac:Company/cac:PartyLegalEntity/cbc:CompanyID/text()",
                namespaces=namespaces,
            )

            if touchpoint_id and org_name:
                party = {"id": touchpoint_id[0], "name": org_name[0]}
                if part_name:
                    party["name"] += f" - {part_name[0]}"
                if company_id:
                    party["identifier"] = {"id": company_id[0], "scheme": "internal"}
                result["parties"].append(party)

    return result if result["parties"] else None


def merge_organization_touchpoint_part_name(
    release_json: dict[str, Any],
    organization_touchpoint_part_name_data: dict[str, Any] | None,
) -> None:
    """Merge organization touchpoint part names into the release JSON.

    Args:
        release_json (Dict[str, Any]): The release JSON to update
        organization_touchpoint_part_name_data (Optional[Dict[str, Any]]): Organization data to merge

    """
    if not organization_touchpoint_part_name_data:
        logger.info("No organization touchpoint part name data to merge")
        return

    existing_parties = release_json.setdefault("parties", [])

    for new_party in organization_touchpoint_part_name_data["parties"]:
        existing_party = next(
            (party for party in existing_parties if party["id"] == new_party["id"]),
            None,
        )
        if existing_party:
            existing_party.update(new_party)
        else:
            existing_parties.append(new_party)

    logger.info(
        "Merged organization touchpoint part name data for %d parties",
        len(organization_touchpoint_part_name_data["parties"]),
    )
