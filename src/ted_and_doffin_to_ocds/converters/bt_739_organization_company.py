# converters/bt_739_organization_company.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)

NAMESPACES = {
    "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
    "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
    "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
    "efext": "http://data.europa.eu/p27/eforms-ubl-extensions/1",
}


def parse_organization_contact_fax(xml_content: str | bytes) -> dict | None:
    """
    Parse BT-739: Organization contact fax number.

    Extracts fax numbers for contacting organizations, following data protection
    regulations regarding personal information.

    Args:
        xml_content: XML content to parse, either as string or bytes

    Returns:
        Optional[Dict]: Parsed data in format:
            {
                "parties": [
                    {
                        "id": str,
                        "contactPoint": {
                            "faxNumber": str
                        }
                    }
                ]
            }
        Returns None if no relevant data found or on error
    """
    try:
        if isinstance(xml_content, str):
            xml_content = xml_content.encode("utf-8")
        root = etree.fromstring(xml_content)
        result = {"parties": []}

        companies = root.xpath(
            "/*/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent"
            "/efext:EformsExtension/efac:Organizations/efac:Organization/efac:Company",
            namespaces=NAMESPACES,
        )

        for company in companies:
            org_id = company.xpath(
                "cac:PartyIdentification/cbc:ID[@schemeName='organization']/text()",
                namespaces=NAMESPACES,
            )
            fax_number = company.xpath(
                "cac:Contact/cbc:Telefax/text()",
                namespaces=NAMESPACES,
            )

            if org_id and fax_number:
                fax = fax_number[0].strip()
                logger.info("Found fax number %s for organization %s", fax, org_id[0])
                party_data = {"id": org_id[0], "contactPoint": {"faxNumber": fax}}
                result["parties"].append(party_data)

        return result if result["parties"] else None

    except etree.XMLSyntaxError:
        logger.exception("Failed to parse XML content")
        raise
    except Exception:
        logger.exception("Error processing organization contact fax")
        return None


def merge_organization_contact_fax(
    release_json: dict, org_fax_data: dict | None
) -> None:
    """
    Merge organization fax number data into the release JSON.

    Updates or adds fax numbers to organization contact points.

    Args:
        release_json: Main OCDS release JSON to update
        org_fax_data: Organization fax data to merge, can be None

    Note:
        - Updates release_json in-place
        - Creates parties array if needed
        - Updates existing organizations' contactPoint
    """
    if not org_fax_data:
        logger.warning("No organization contact fax data to merge")
        return

    parties = release_json.setdefault("parties", [])

    for new_party in org_fax_data["parties"]:
        existing_party = next(
            (party for party in parties if party["id"] == new_party["id"]), None
        )
        if existing_party:
            contact_point = existing_party.setdefault("contactPoint", {})
            contact_point["faxNumber"] = new_party["contactPoint"]["faxNumber"]
        else:
            parties.append(new_party)

    logger.info(
        "Merged organization contact fax data for %d organizations",
        len(org_fax_data["parties"]),
    )
