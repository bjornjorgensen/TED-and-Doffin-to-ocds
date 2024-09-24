# converters/bt_739_organization_company.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)


def parse_organization_contact_fax(xml_content):
    """
    Parse the XML content to extract the organization contact fax number.

    Args:
        xml_content (str or bytes): The XML content to parse.

    Returns:
        dict: A dictionary containing the parsed organization contact fax number.
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

    xpath_query = "//efac:organization/efac:company"
    companies = root.xpath(xpath_query, namespaces=namespaces)

    for company in companies:
        org_id = company.xpath(
            "cac:partyIdentification/cbc:ID[@schemeName='organization']/text()",
            namespaces=namespaces,
        )
        fax_number = company.xpath(
            "cac:Contact/cbc:Telefax/text()",
            namespaces=namespaces,
        )

        if org_id and fax_number:
            party_data = {"id": org_id[0], "contactPoint": {"faxNumber": fax_number[0]}}
            result["parties"].append(party_data)

    return result if result["parties"] else None


def merge_organization_contact_fax(release_json, organization_fax_data):
    """
    Merge the parsed organization contact fax number into the main OCDS release JSON.

    Args:
        release_json (dict): The main OCDS release JSON to be updated.
        organization_fax_data (dict): The parsed organization contact fax data to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not organization_fax_data:
        logger.warning("No organization contact fax data to merge")
        return

    parties = release_json.setdefault("parties", [])

    for new_party in organization_fax_data["parties"]:
        existing_party = next(
            (party for party in parties if party["id"] == new_party["id"]),
            None,
        )
        if existing_party:
            existing_party.setdefault("contactPoint", {}).update(
                new_party["contactPoint"],
            )
        else:
            parties.append(new_party)

    logger.info(
        "Merged organization contact fax data for %d organizations",
        len(organization_fax_data["parties"]),
    )
