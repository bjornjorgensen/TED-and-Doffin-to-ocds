import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_organization_edelivery_gateway(
    xml_content: str | bytes,
) -> dict | None:
    """
    Parse organization eDelivery gateway information from XML content.

    Args:
        xml_content (Union[str, bytes]): The XML content containing organization endpoint information

    Returns:
        Optional[Dict]: A dictionary containing parsed eDelivery gateway data in OCDS format with
        'parties' array, or None if no valid endpoint data is found.
        Example:
        {
            "parties": [{
                "id": "ORG-0001",
                "eDeliveryGateway": "https://drive.xpertpro.eu"
            }]
        }
    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")
    root = etree.fromstring(xml_content)
    namespaces = {
        "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
        "efext": "http://data.europa.eu/p27/eforms-ubl-extensions/1",
        "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
        "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
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
        endpoint_id = org.xpath(
            "efac:Company/cbc:EndpointID/text()",
            namespaces=namespaces,
        )

        if org_id and endpoint_id:
            result["parties"].append(
                {"id": org_id[0], "eDeliveryGateway": endpoint_id[0]},
            )
            logger.info("Found eDelivery gateway for organization %s", org_id[0])

    return result if result["parties"] else None


def merge_organization_edelivery_gateway(
    release_json: dict, edelivery_gateway_data: dict | None
) -> None:
    """
    Merge organization eDelivery gateway data into the release JSON.

    Args:
        release_json (Dict): The target release JSON to merge data into
        edelivery_gateway_data (Optional[Dict]): Organization endpoint data to merge,
            containing a 'parties' array with eDelivery gateway information

    Returns:
        None: Modifies release_json in place

    Note:
        If edelivery_gateway_data is None or contains no parties, no changes are made.
        For existing parties, eDeliveryGateway information is updated with new values.
    """
    if not edelivery_gateway_data:
        logger.info("No eDelivery gateway data to merge")
        return

    existing_parties = release_json.setdefault("parties", [])

    for new_party in edelivery_gateway_data["parties"]:
        existing_party = next(
            (party for party in existing_parties if party["id"] == new_party["id"]),
            None,
        )
        if existing_party:
            existing_party["eDeliveryGateway"] = new_party["eDeliveryGateway"]
            logger.info("Updated eDelivery gateway for party %s", new_party["id"])
        else:
            existing_parties.append(new_party)
            logger.info("Added new party with eDelivery gateway: %s", new_party["id"])
