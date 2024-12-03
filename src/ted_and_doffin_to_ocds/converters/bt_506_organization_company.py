# converters/bt_506_organization_company.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_organization_email(xml_content: str | bytes) -> dict | None:
    """
    Parse organization email contact information from XML content.

    Args:
        xml_content (Union[str, bytes]): The XML content containing organization email information

    Returns:
        Optional[Dict]: A dictionary containing parsed email data in OCDS format with
        'parties' array, or None if no valid email data is found.
        Example:
        {
            "parties": [{
                "id": "ORG-0001",
                "contactPoint": {
                    "email": "press@xyz.europa.eu"
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
        email = org.xpath(
            "efac:Company/cac:Contact/cbc:ElectronicMail/text()", namespaces=namespaces
        )

        if org_id and email:
            party = {"id": org_id[0], "contactPoint": {"email": email[0]}}
            result["parties"].append(party)

    return result if result["parties"] else None


def merge_organization_email(
    release_json: dict, organization_email_data: dict | None
) -> None:
    """
    Merge organization email data into the release JSON.

    Args:
        release_json (Dict): The target release JSON to merge data into
        organization_email_data (Optional[Dict]): Organization email data to merge,
            containing a 'parties' array with contact information

    Returns:
        None: Modifies release_json in place

    Note:
        If organization_email_data is None or contains no parties, no changes are made.
        For existing parties, email contact information is updated with new values.
    """
    if not organization_email_data:
        logger.info("No organization email data to merge")
        return

    existing_parties = release_json.setdefault("parties", [])

    for new_party in organization_email_data["parties"]:
        existing_party = next(
            (party for party in existing_parties if party["id"] == new_party["id"]),
            None,
        )
        if existing_party:
            existing_party.setdefault("contactPoint", {}).update(
                new_party["contactPoint"]
            )
        else:
            existing_parties.append(new_party)

    logger.info(
        "Merged organization email data for %d parties",
        len(organization_email_data["parties"]),
    )
