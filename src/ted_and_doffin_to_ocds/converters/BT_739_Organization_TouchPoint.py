# converters/BT_739_Organization_TouchPoint.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)


def parse_touchpoint_contact_fax(xml_content):
    """
    Parse the XML content to extract the touchpoint contact fax number.

    Args:
        xml_content (str or bytes): The XML content to parse.

    Returns:
        dict: A dictionary containing the parsed touchpoint contact fax number.
        None: If no relevant data is found.
    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")
    root = etree.fromstring(xml_content)
    namespaces = {
        "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
        "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
        "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
        "efext": "http://data.europa.eu/p27/eforms-ubl-extensions/1",
        "efbc": "http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1",
    }

    result = {"parties": []}

    xpath_query = "//efac:Organization"
    organizations = root.xpath(xpath_query, namespaces=namespaces)

    for organization in organizations:
        company_id = organization.xpath(
            "efac:Company/cac:PartyLegalEntity/cbc:CompanyID/text()",
            namespaces=namespaces,
        )
        touchpoint = organization.xpath("efac:TouchPoint", namespaces=namespaces)

        if touchpoint:
            touchpoint_id = touchpoint[0].xpath(
                "cac:PartyIdentification/cbc:ID[@schemeName='touchpoint']/text()",
                namespaces=namespaces,
            )
            fax_number = touchpoint[0].xpath(
                "cac:Contact/cbc:Telefax/text()",
                namespaces=namespaces,
            )

            if touchpoint_id and fax_number:
                party_data = {
                    "id": touchpoint_id[0],
                    "contactPoint": {"faxNumber": fax_number[0]},
                }
                if company_id:
                    party_data["identifier"] = {"id": company_id[0], "scheme": "GB-COH"}
                result["parties"].append(party_data)

    return result if result["parties"] else None


def merge_touchpoint_contact_fax(release_json, touchpoint_fax_data):
    """
    Merge the parsed touchpoint contact fax number into the main OCDS release JSON.

    Args:
        release_json (dict): The main OCDS release JSON to be updated.
        touchpoint_fax_data (dict): The parsed touchpoint contact fax data to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not touchpoint_fax_data:
        logger.warning("No touchpoint contact fax data to merge")
        return

    parties = release_json.setdefault("parties", [])

    for new_party in touchpoint_fax_data["parties"]:
        existing_party = next(
            (party for party in parties if party["id"] == new_party["id"]),
            None,
        )
        if existing_party:
            existing_party.setdefault("contactPoint", {}).update(
                new_party["contactPoint"],
            )
            if "identifier" in new_party:
                existing_party["identifier"] = new_party["identifier"]
        else:
            parties.append(new_party)

    logger.info(
        f"Merged touchpoint contact fax data for {len(touchpoint_fax_data['parties'])} touchpoints",
    )
