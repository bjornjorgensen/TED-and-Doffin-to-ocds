# converters/BT_739_UBO.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)


def parse_ubo_fax(xml_content):
    """
    Parse the XML content to extract the UBO fax number.

    Args:
        xml_content (str or bytes): The XML content to parse.

    Returns:
        dict: A dictionary containing the parsed UBO fax number.
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

    xpath_query = "//efac:Organizations"
    organizations = root.xpath(xpath_query, namespaces=namespaces)

    for org in organizations:
        company = org.xpath("efac:Organization/efac:Company", namespaces=namespaces)
        if company:
            org_id = company[0].xpath(
                "cac:PartyIdentification/cbc:ID[@schemeName='organization']/text()",
                namespaces=namespaces,
            )
            if org_id:
                ubo_data = []
                ubos = org.xpath("efac:UltimateBeneficialOwner", namespaces=namespaces)
                for ubo in ubos:
                    ubo_id = ubo.xpath(
                        "cbc:ID[@schemeName='ubo']/text()",
                        namespaces=namespaces,
                    )
                    fax_number = ubo.xpath(
                        "cac:Contact/cbc:Telefax/text()",
                        namespaces=namespaces,
                    )
                    if ubo_id and fax_number:
                        ubo_data.append({"id": ubo_id[0], "faxNumber": fax_number[0]})
                if ubo_data:
                    result["parties"].append(
                        {"id": org_id[0], "beneficialOwners": ubo_data},
                    )

    return result if result["parties"] else None


def merge_ubo_fax(release_json, ubo_fax_data):
    """
    Merge the parsed UBO fax number into the main OCDS release JSON.

    Args:
        release_json (dict): The main OCDS release JSON to be updated.
        ubo_fax_data (dict): The parsed UBO fax data to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not ubo_fax_data:
        logger.warning("No UBO fax data to merge")
        return

    parties = release_json.setdefault("parties", [])

    for new_party in ubo_fax_data["parties"]:
        existing_party = next(
            (party for party in parties if party["id"] == new_party["id"]),
            None,
        )
        if existing_party:
            existing_beneficial_owners = existing_party.setdefault(
                "beneficialOwners",
                [],
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
            parties.append(new_party)

    logger.info(f"Merged UBO fax data for {len(ubo_fax_data['parties'])} organizations")
