# converters/bt_500_ubo.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_ubo_name(xml_content: str | bytes) -> dict | None:
    """Parse the beneficial owner names from XML data.

    Args:
        xml_content (Union[str, bytes]): The XML content containing organization information

    Returns:
        Optional[Dict]: Dictionary containing party information, or None if no data found
        The structure follows the format:
        {
            "parties": [
                {
                    "id": str,
                    "beneficialOwners": [
                        {
                            "id": str,
                            "name": str
                        }
                    ]
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
        if org_id:
            party = {"id": org_id[0], "beneficialOwners": []}

            ubos = root.xpath(
                "//efac:Organizations/efac:UltimateBeneficialOwner",
                namespaces=namespaces,
            )
            for ubo in ubos:
                ubo_id = ubo.xpath(
                    "cbc:ID[@schemeName='ubo']/text()", namespaces=namespaces
                )
                ubo_name = ubo.xpath("cbc:FamilyName/text()", namespaces=namespaces)
                if ubo_id and ubo_name:
                    party["beneficialOwners"].append(
                        {"id": ubo_id[0], "name": ubo_name[0]}
                    )

            if party["beneficialOwners"]:
                result["parties"].append(party)

    return result if result["parties"] else None


def merge_ubo_name(release_json: dict, ubo_name_data: dict | None) -> None:
    """Merge beneficial owner name data into the release JSON.

    Args:
        release_json (Dict): The target release JSON to merge data into
        ubo_name_data (Optional[Dict]): The source data containing parties
            to be merged. If None, function returns without making changes.

    Note:
        The function modifies release_json in-place by adding or updating the
        parties.beneficialOwners field for matching parties.

    """
    if not ubo_name_data:
        logger.info("No UBO name data to merge")
        return

    existing_parties = release_json.setdefault("parties", [])

    for new_party in ubo_name_data["parties"]:
        existing_party = next(
            (party for party in existing_parties if party["id"] == new_party["id"]),
            None,
        )
        if existing_party:
            existing_beneficial_owners = existing_party.setdefault(
                "beneficialOwners", []
            )
            for new_ubo in new_party["beneficialOwners"]:
                existing_ubo = next(
                    (
                        ubo
                        for ubo in existing_beneficial_owners
                        if ubo["id"] == new_ubo["id"]
                    ),
                    None,
                )
                if existing_ubo:
                    existing_ubo.update(new_ubo)
                else:
                    existing_beneficial_owners.append(new_ubo)
        else:
            existing_parties.append(new_party)

    logger.info("Merged UBO name data for %d parties", len(ubo_name_data["parties"]))
