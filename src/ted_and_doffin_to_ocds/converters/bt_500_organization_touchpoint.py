import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_organization_touchpoint_name(
    xml_content: str | bytes,
) -> dict | None:
    """
    Parse organization touchpoint names from XML data.

    Args:
        xml_content (Union[str, bytes]): The XML content containing organization information

    Returns:
        Optional[Dict]: Dictionary containing party information, or None if no data found
        The structure follows the format:
        {
            "parties": [
                {
                    "id": str,
                    "name": str,
                    "identifier": {  # Optional
                        "id": str,
                        "scheme": "internal"
                    }
                }
            ]
        }
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

    organizations = root.xpath(
        "/*/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:Organizations/efac:Organization",
        namespaces=namespaces,
    )

    for org in organizations:
        touchpoint = org.xpath("efac:TouchPoint", namespaces=namespaces)
        if touchpoint:
            touchpoint = touchpoint[0]
            touchpoint_id = touchpoint.xpath(
                "cac:PartyIdentification/cbc:ID[@schemeName='touchpoint']/text()",
                namespaces=namespaces,
            )
            org_name = touchpoint.xpath(
                "cac:PartyName/cbc:Name/text()", namespaces=namespaces
            )
            company_id = org.xpath(
                "efac:Company/cac:PartyLegalEntity/cbc:CompanyID/text()",
                namespaces=namespaces,
            )

            if touchpoint_id and org_name:
                party = {"id": touchpoint_id[0], "name": org_name[0]}
                if company_id:
                    party["identifier"] = {"id": company_id[0], "scheme": "internal"}
                result["parties"].append(party)

    return result if result["parties"] else None


def merge_organization_touchpoint_name(
    release_json: dict, organization_touchpoint_name_data: dict | None
) -> None:
    """
    Merge organization touchpoint name data into the release JSON.

    Args:
        release_json (Dict): The target release JSON to merge data into
        organization_touchpoint_name_data (Optional[Dict]): The source data containing parties
            to be merged. If None, function returns without making changes.
    """
    if not organization_touchpoint_name_data:
        return

    existing_parties = release_json.setdefault("parties", [])
    for new_party in organization_touchpoint_name_data["parties"]:
        existing_party = next(
            (p for p in existing_parties if p["id"] == new_party["id"]),
            None,
        )
        if existing_party:
            existing_party.update(new_party)
        else:
            existing_parties.append(new_party)

    logger.info(
        "Merged organization touchpoint name data for %d parties",
        len(organization_touchpoint_name_data["parties"]),
    )
