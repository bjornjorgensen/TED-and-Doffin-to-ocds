import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_touchpoint_edelivery_gateway(
    xml_content: str | bytes,
) -> dict | None:
    """Parse touchpoint eDelivery gateway information from XML content.

    Args:
        xml_content (Union[str, bytes]): The XML content containing touchpoint endpoint information

    Returns:
        Optional[Dict]: A dictionary containing parsed eDelivery gateway data in OCDS format with
        'parties' array, or None if no valid endpoint data is found.

    Example:
        {
            "parties": [{
                "id": "TPO-0001",
                "eDeliveryGateway": "https://drive.xpertpro.eu",
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
        touchpoint = org.xpath("efac:TouchPoint", namespaces=namespaces)
        if touchpoint:
            touchpoint = touchpoint[0]
            touchpoint_id = touchpoint.xpath(
                "cac:PartyIdentification/cbc:ID[@schemeName='touchpoint']/text()",
                namespaces=namespaces,
            )
            endpoint_id = touchpoint.xpath(
                "cbc:EndpointID/text()", namespaces=namespaces
            )
            company_id = org.xpath(
                "efac:Company/cac:PartyLegalEntity/cbc:CompanyID/text()",
                namespaces=namespaces,
            )

            if touchpoint_id and endpoint_id:
                party = {"id": touchpoint_id[0], "eDeliveryGateway": endpoint_id[0]}
                if company_id:
                    party["identifier"] = {"id": company_id[0], "scheme": "internal"}
                result["parties"].append(party)
                logger.info(
                    "Found eDelivery gateway for touchpoint %s", touchpoint_id[0]
                )

    return result if result["parties"] else None


def merge_touchpoint_edelivery_gateway(
    release_json: dict, edelivery_gateway_data: dict | None
) -> None:
    """Merge touchpoint eDelivery gateway data into the release JSON.

    Args:
        release_json (Dict): The target release JSON to merge data into
        edelivery_gateway_data (Optional[Dict]): Touchpoint endpoint data to merge,
            containing a 'parties' array with eDelivery gateway and identifier information

    Returns:
        None: Modifies release_json in place

    Note:
        If edelivery_gateway_data is None or contains no parties, no changes are made.
        For existing parties, both eDeliveryGateway and identifier information is updated.

    """
    if not edelivery_gateway_data:
        logger.info("No touchpoint eDelivery gateway data to merge")
        return

    existing_parties = release_json.setdefault("parties", [])

    for new_party in edelivery_gateway_data["parties"]:
        existing_party = next(
            (party for party in existing_parties if party["id"] == new_party["id"]),
            None,
        )
        if existing_party:
            existing_party["eDeliveryGateway"] = new_party["eDeliveryGateway"]
            if "identifier" in new_party:
                existing_party["identifier"] = new_party["identifier"]
            logger.info("Updated eDelivery gateway for touchpoint %s", new_party["id"])
        else:
            existing_parties.append(new_party)
            logger.info(
                "Added new touchpoint with eDelivery gateway: %s", new_party["id"]
            )
