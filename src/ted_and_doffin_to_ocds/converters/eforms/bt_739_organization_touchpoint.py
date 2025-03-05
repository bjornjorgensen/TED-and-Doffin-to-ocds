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


def parse_touchpoint_contact_fax(xml_content: str | bytes) -> dict | None:
    """Parse BT-739: Organization touchpoint contact fax number.

    Extracts fax numbers for contacting organizations via their touchpoints,
    following data protection regulations regarding personal information.

    Args:
        xml_content: XML content to parse, either as string or bytes

    Returns:
        Optional[Dict]: Parsed data in format:
            {
                "parties": [
                    {
                        "id": str,  # touchpoint ID
                        "identifier": {  # optional
                            "id": str,
                            "scheme": "GB-COH"
                        },
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

        organizations = root.xpath(
            "/*/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent"
            "/efext:EformsExtension/efac:Organizations/efac:Organization",
            namespaces=NAMESPACES,
        )

        for org in organizations:
            company_id = org.xpath(
                "efac:Company/cac:PartyLegalEntity/cbc:companyID/text()",
                namespaces=NAMESPACES,
            )

            touchpoints = org.xpath("efac:TouchPoint", namespaces=NAMESPACES)
            for touchpoint in touchpoints:
                tp_id = touchpoint.xpath(
                    "cac:PartyIdentification/cbc:ID[@schemeName='touchpoint']/text()",
                    namespaces=NAMESPACES,
                )
                fax = touchpoint.xpath(
                    "cac:Contact/cbc:Telefax/text()",
                    namespaces=NAMESPACES,
                )

                if tp_id and fax:
                    party_data = {
                        "id": tp_id[0],
                        "contactPoint": {"faxNumber": fax[0].strip()},
                    }
                    if company_id:
                        party_data["identifier"] = {
                            "id": company_id[0].strip(),
                            "scheme": "GB-COH",
                        }
                    logger.info(
                        "Found fax number for touchpoint %s: %s",
                        tp_id[0],
                        fax[0].strip(),
                    )
                    result["parties"].append(party_data)

        return result if result["parties"] else None

    except etree.XMLSyntaxError:
        logger.exception("Failed to parse XML content")
        raise
    except Exception:
        logger.exception("Error processing touchpoint contact fax")
        return None


def merge_touchpoint_contact_fax(
    release_json: dict, touchpoint_data: dict | None
) -> None:
    """Merge touchpoint fax number data into the release JSON.

    Updates or adds fax numbers to organization touchpoint contact points.

    Args:
        release_json: Main OCDS release JSON to update
        touchpoint_data: Touchpoint fax data to merge, can be None

    Note:
        - Updates release_json in-place
        - Creates parties array if needed
        - Updates existing touchpoints' contactPoint
        - Preserves existing identifiers

    """
    if not touchpoint_data:
        logger.warning("No touchpoint contact fax data to merge")
        return

    parties = release_json.setdefault("parties", [])

    for new_party in touchpoint_data["parties"]:
        existing_party = next(
            (party for party in parties if party["id"] == new_party["id"]), None
        )
        if existing_party:
            contact_point = existing_party.setdefault("contactPoint", {})
            contact_point["faxNumber"] = new_party["contactPoint"]["faxNumber"]
            if "identifier" in new_party:
                existing_party["identifier"] = new_party["identifier"]
        else:
            parties.append(new_party)

    logger.info(
        "Merged touchpoint contact fax data for %d touchpoints",
        len(touchpoint_data["parties"]),
    )
