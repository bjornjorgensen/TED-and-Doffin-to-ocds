# converters/bt_746_organization.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)

NAMESPACES = {
    "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
    "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
    "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
    "efext": "http://data.europa.eu/p27/eforms-ubl-extensions/1",
    "efbc": "http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1",
}


def parse_organization_regulated_market(
    xml_content: str | bytes,
) -> dict | None:
    """
    Parse BT-746: Organization regulated market listing status.

    Determines if organization is listed on a regulated market that ensures adequate
    transparency under anti-money laundering legislation.

    Args:
        xml_content: XML content to parse, either as string or bytes

    Returns:
        Optional[Dict]: Parsed data in format:
            {
                "parties": [
                    {
                        "id": str,
                        "details": {
                            "listedOnRegulatedMarket": bool
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
            listed_indicator = org.xpath(
                "efbc:ListedOnRegulatedMarketIndicator/text()", namespaces=NAMESPACES
            )
            org_id = org.xpath(
                "efac:Company/cac:PartyIdentification/cbc:ID[@schemeName='organization']/text()",
                namespaces=NAMESPACES,
            )

            if listed_indicator and org_id:
                is_listed = listed_indicator[0].lower() == "true"
                logger.info(
                    "Found regulated market status %s for organization %s",
                    is_listed,
                    org_id[0],
                )
                party_data = {
                    "id": org_id[0],
                    "details": {"listedOnRegulatedMarket": is_listed},
                }
                result["parties"].append(party_data)

        return result if result["parties"] else None

    except etree.XMLSyntaxError:
        logger.exception("Failed to parse XML content")
        raise
    except Exception:
        logger.exception("Error processing regulated market status")
        return None


def merge_organization_regulated_market(
    release_json: dict, market_data: dict | None
) -> None:
    """
    Merge regulated market status data into the release JSON.

    Updates or adds regulated market status to organization details.

    Args:
        release_json: Main OCDS release JSON to update
        market_data: Regulated market status data to merge, can be None

    Note:
        - Updates release_json in-place
        - Creates parties array if needed
        - Updates existing parties' details
    """
    if not market_data:
        logger.warning("No regulated market status data to merge")
        return

    parties = release_json.setdefault("parties", [])

    for new_party in market_data["parties"]:
        existing_party = next((p for p in parties if p["id"] == new_party["id"]), None)
        if existing_party:
            details = existing_party.setdefault("details", {})
            details["listedOnRegulatedMarket"] = new_party["details"][
                "listedOnRegulatedMarket"
            ]
        else:
            parties.append(new_party)

    logger.info(
        "Merged regulated market status data for %d organizations",
        len(market_data["parties"]),
    )
