# converters/bt_505_organization_touchpoint.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_touchpoint_website(xml_content: str | bytes) -> dict | None:
    """
    Parse touchpoint website information from XML content.

    Args:
        xml_content (Union[str, bytes]): The XML content containing touchpoint website information

    Returns:
        Optional[Dict]: A dictionary containing parsed website data in OCDS format with
        'parties' array, or None if no valid touchpoint data is found.
        Example:
        {
            "parties": [{
                "id": "TPO-0001",
                "details": {
                    "url": "http://abc.europa.eu/"
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
            website = touchpoint.xpath("cbc:WebsiteURI/text()", namespaces=namespaces)
            company_id = org.xpath(
                "efac:Company/cac:PartyLegalEntity/cbc:CompanyID/text()",
                namespaces=namespaces,
            )

            if touchpoint_id and website:
                party = {"id": touchpoint_id[0], "details": {"url": website[0]}}
                if company_id:
                    party["identifier"] = {"id": company_id[0], "scheme": "internal"}
                result["parties"].append(party)

    return result if result["parties"] else None


def merge_touchpoint_website(
    release_json: dict, touchpoint_website_data: dict | None
) -> None:
    """
    Merge touchpoint website data into the release JSON.

    Args:
        release_json (Dict): The target release JSON to merge data into
        touchpoint_website_data (Optional[Dict]): Touchpoint website data to merge,
            containing a 'parties' array with website and identifier information

    Returns:
        None: Modifies release_json in place

    Note:
        If touchpoint_website_data is None or contains no parties, no changes are made.
        For existing parties, both website url and identifier information is updated.
    """
    if not touchpoint_website_data:
        logger.info("No touchpoint website data to merge")
        return

    existing_parties = release_json.setdefault("parties", [])

    for new_party in touchpoint_website_data["parties"]:
        existing_party = next(
            (party for party in existing_parties if party["id"] == new_party["id"]),
            None,
        )
        if existing_party:
            existing_party.setdefault("details", {}).update(new_party["details"])
            if "identifier" in new_party:
                existing_party["identifier"] = new_party["identifier"]
        else:
            existing_parties.append(new_party)

    logger.info(
        "Merged touchpoint website data for %d parties",
        len(touchpoint_website_data["parties"]),
    )
