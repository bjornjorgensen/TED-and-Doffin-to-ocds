# converters/bt_505_organization_company.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_organization_website(xml_content: str | bytes) -> dict | None:
    """
    Parse organization website information from XML content.

    Args:
        xml_content (Union[str, bytes]): The XML content containing organization website information

    Returns:
        Optional[Dict]: A dictionary containing parsed website data in OCDS format with
        'parties' array, or None if no valid website data is found.
        Example:
        {
            "parties": [{
                "id": "ORG-0001",
                "details": {
                    "url": "http://xyz.europa.eu/"
                }
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
        website = org.xpath("efac:Company/cbc:WebsiteURI/text()", namespaces=namespaces)

        if org_id and website:
            party = {"id": org_id[0], "details": {"url": website[0]}}
            result["parties"].append(party)

    return result if result["parties"] else None


def merge_organization_website(
    release_json: dict, organization_website_data: dict | None
) -> None:
    """
    Merge organization website data into the release JSON.

    Args:
        release_json (Dict): The target release JSON to merge data into
        organization_website_data (Optional[Dict]): Organization website data to merge,
            containing a 'parties' array with website information

    Returns:
        None: Modifies release_json in place

    Note:
        If organization_website_data is None or contains no parties, no changes are made.
        For existing parties, website information is updated in the details section.
    """
    if not organization_website_data:
        logger.info("No organization website data to merge")
        return

    existing_parties = release_json.setdefault("parties", [])

    for new_party in organization_website_data["parties"]:
        existing_party = next(
            (party for party in existing_parties if party["id"] == new_party["id"]),
            None,
        )
        if existing_party:
            existing_party.setdefault("details", {}).update(new_party["details"])
        else:
            existing_parties.append(new_party)

    logger.info(
        "Merged organization website data for %d parties",
        len(organization_website_data["parties"]),
    )
