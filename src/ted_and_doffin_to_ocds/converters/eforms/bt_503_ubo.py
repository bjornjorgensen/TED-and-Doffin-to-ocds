# converters/bt_503_ubo.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_ubo_telephone(xml_content: str | bytes) -> dict | None:
    """Parse UBO (Ultimate Beneficial Owner) telephone information from XML content.

    Args:
        xml_content (Union[str, bytes]): The XML content containing UBO telephone information

    Returns:
        Optional[Dict]: A dictionary containing parsed UBO telephone data in OCDS format with
        'parties' array, or None if no valid UBO data is found.

    Example:
        {
            "parties": [{
                "id": "ORG-0001",
                "beneficialOwners": [{
                    "id": "UBO-0001",
                    "telephone": "+123 456789"
                }]
            }]
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
                ubo_telephone = ubo.xpath("cbc:Telephone/text()", namespaces=namespaces)
                if ubo_id and ubo_telephone:
                    party["beneficialOwners"].append(
                        {"id": ubo_id[0], "telephone": ubo_telephone[0]}
                    )

            if party["beneficialOwners"]:
                result["parties"].append(party)

    return result if result["parties"] else None


def merge_ubo_telephone(release_json: dict, ubo_telephone_data: dict | None) -> None:
    """Merge UBO telephone data into the release JSON.

    Args:
        release_json (Dict): The target release JSON to merge data into
        ubo_telephone_data (Optional[Dict]): UBO telephone data to merge,
            containing a 'parties' array with beneficial owner information

    Returns:
        None: Modifies release_json in place

    Note:
        If ubo_telephone_data is None or contains no parties, no changes are made.
        For existing parties, beneficial owner telephone information is updated or added.

    """
    if not ubo_telephone_data:
        logger.info("No UBO telephone data to merge")
        return

    existing_parties = release_json.setdefault("parties", [])

    for new_party in ubo_telephone_data["parties"]:
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

    logger.info(
        "Merged UBO telephone data for %d parties", len(ubo_telephone_data["parties"])
    )
