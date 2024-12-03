import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_organization_name(xml_content: str | bytes) -> dict | None:
    """
    Parse organization names from XML data.

    Args:
        xml_content (Union[str, bytes]): The XML content containing organization information

    Returns:
        Optional[Dict]: Dictionary containing party information, or None if no data found
        The structure follows the format:
        {
            "parties": [
                {
                    "id": str,
                    "name": str
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
        org_id = org.xpath(
            "efac:Company/cac:PartyIdentification/cbc:ID[@schemeName='organization']/text()",
            namespaces=namespaces,
        )
        org_name = org.xpath(
            "efac:Company/cac:PartyName/cbc:Name/text()",
            namespaces=namespaces,
        )

        if org_id and org_name:
            party = {"id": org_id[0], "name": org_name[0]}
            result["parties"].append(party)

    return result if result["parties"] else None


def merge_organization_name(
    release_json: dict, organization_name_data: dict | None
) -> None:
    """
    Merge organization name data into the release JSON.

    Args:
        release_json (Dict): The target release JSON to merge data into
        organization_name_data (Optional[Dict]): The source data containing parties
            to be merged. If None, function returns without making changes.
    """
    if not organization_name_data:
        return

    existing_parties = release_json.setdefault("parties", [])
    for new_party in organization_name_data["parties"]:
        existing_party = next(
            (p for p in existing_parties if p["id"] == new_party["id"]),
            None,
        )
        if existing_party:
            existing_party["name"] = new_party["name"]
        else:
            existing_parties.append(new_party)
