# converters/bt_506_organization_touchpoint.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_touchpoint_email(xml_content: str | bytes) -> dict | None:
    """Parse touchpoint email contact information from XML content.

    Args:
        xml_content (Union[str, bytes]): The XML content containing touchpoint email information

    Returns:
        Optional[Dict]: A dictionary containing parsed email data in OCDS format with
        'parties' array, or None if no valid touchpoint data is found.

    Example:
        {
            "parties": [{
                "id": "TPO-0001",
                "contactPoint": {
                    "email": "abc@xyz.europa.eu"
                },
                "identifier": {
                    "id": "998298",
                    "scheme": "internal"
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
        touchpoint = org.xpath("efac:TouchPoint", namespaces=namespaces)
        if touchpoint:
            touchpoint = touchpoint[0]
            touchpoint_id = touchpoint.xpath(
                "cac:PartyIdentification/cbc:ID[@schemeName='touchpoint']/text()",
                namespaces=namespaces,
            )
            email = touchpoint.xpath(
                "cac:Contact/cbc:ElectronicMail/text()", namespaces=namespaces
            )
            company_id = org.xpath(
                "efac:Company/cac:PartyLegalEntity/cbc:CompanyID/text()",
                namespaces=namespaces,
            )

            if touchpoint_id and email:
                party = {"id": touchpoint_id[0], "contactPoint": {"email": email[0]}}
                if company_id:
                    party["identifier"] = {"id": company_id[0], "scheme": "internal"}
                result["parties"].append(party)

    return result if result["parties"] else None


def merge_touchpoint_email(
    release_json: dict, touchpoint_email_data: dict | None
) -> None:
    """Merge touchpoint email data into the release JSON.

    Args:
        release_json (Dict): The target release JSON to merge data into
        touchpoint_email_data (Optional[Dict]): Touchpoint email data to merge,
            containing a 'parties' array with contact and identifier information

    Returns:
        None: Modifies release_json in place

    Note:
        If touchpoint_email_data is None or contains no parties, no changes are made.
        For existing parties, both email contact and identifier information is updated.

    """
    if not touchpoint_email_data:
        logger.info("No touchpoint email data to merge")
        return

    existing_parties = release_json.setdefault("parties", [])

    for new_party in touchpoint_email_data["parties"]:
        existing_party = next(
            (party for party in existing_parties if party["id"] == new_party["id"]),
            None,
        )
        if existing_party:
            existing_party.setdefault("contactPoint", {}).update(
                new_party["contactPoint"]
            )
            if "identifier" in new_party:
                existing_party["identifier"] = new_party["identifier"]
        else:
            existing_parties.append(new_party)

    logger.info(
        "Merged touchpoint email data for %d parties",
        len(touchpoint_email_data["parties"]),
    )