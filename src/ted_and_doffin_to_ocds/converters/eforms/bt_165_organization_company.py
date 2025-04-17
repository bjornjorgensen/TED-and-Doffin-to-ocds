# converters/bt_165_organization_company.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_winner_size(xml_content: str | bytes) -> dict | None:
    """Parse organization size information from XML data.

    Args:
        xml_content (Union[str, bytes]): The XML content containing organization information

    Returns:
        Optional[Dict]: Dictionary containing party information, or None if no data found
        The structure follows the format:
        {
            "parties": [
                {
                    "id": str,
                    "details": {
                        "scale": str
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

    # eForms format parsing
    organizations = root.xpath(
        "//efac:Organizations/efac:Organization",
        namespaces=namespaces,
    )

    for organization in organizations:
        org_id = organization.xpath(
            "efac:Company/cac:PartyIdentification/cbc:ID[@schemeName='organization']/text()",
            namespaces=namespaces,
        )
        company_size = organization.xpath(
            "efac:Company/efbc:CompanySizeCode[@listName='economic-operator-size']/text()",
            namespaces=namespaces,
        )

        if org_id and company_size:
            party = {"id": org_id[0], "details": {"scale": company_size[0]}}
            result["parties"].append(party)
            logger.info(
                "Found organization %s with size %s", org_id[0], company_size[0]
            )

    return result if result["parties"] else None


def merge_winner_size(release_json: dict, winner_size_data: dict | None) -> None:
    """Merge organization size data into the release JSON.

    Args:
        release_json (Dict): The target release JSON to merge data into
        winner_size_data (Optional[Dict]): The source data containing parties
            to be merged. If None, function returns without making changes.

    """
    if not winner_size_data:
        return

    existing_parties = release_json.setdefault("parties", [])
    for new_party in winner_size_data["parties"]:
        existing_party = next(
            (p for p in existing_parties if p["id"] == new_party["id"]),
            None,
        )
        if existing_party:
            existing_party.setdefault("details", {}).update(new_party["details"])
        else:
            existing_parties.append(new_party)

    logger.info(
        "Merged Winner Size data for %d parties",
        len(winner_size_data["parties"]),
    )
