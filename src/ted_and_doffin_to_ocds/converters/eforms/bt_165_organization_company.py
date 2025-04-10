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
        "ted": "http://publications.europa.eu/resource/schema/ted/2016/05/01/ted",
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

    # TED format parsing
    ted_contractors = root.xpath(
        "//ted:FORM_SECTION/ted:F03_2014/ted:AWARD_CONTRACT/ted:AWARDED_CONTRACT/ted:CONTRACTORS/ted:CONTRACTOR"
        " | //ted:FORM_SECTION/ted:F13_2014/ted:RESULTS/ted:AWARDED_PRIZE/ted:WINNERS/ted:WINNER"
        " | //ted:FORM_SECTION/ted:F15_2014/ted:AWARD_CONTRACT/ted:AWARDED_CONTRACT/ted:CONTRACTORS/ted:CONTRACTOR"
        " | //ted:FORM_SECTION/ted:F21_2014/ted:AWARD_CONTRACT/ted:AWARDED_CONTRACT/ted:CONTRACTORS/ted:CONTRACTOR"
        " | //ted:FORM_SECTION/ted:F22_2014/ted:AWARD_CONTRACT/ted:AWARDED_CONTRACT/ted:CONTRACTORS/ted:CONTRACTOR"
        " | //ted:FORM_SECTION/ted:F23_2014/ted:AWARD_CONTRACT/ted:AWARDED_CONTRACT/ted:CONTRACTORS/ted:CONTRACTOR"
        " | //ted:FORM_SECTION/ted:F25_2014/ted:AWARD_CONTRACT/ted:AWARDED_CONTRACT/ted:CONTRACTORS/ted:CONTRACTOR",
        namespaces=namespaces,
    )

    for contractor in ted_contractors:
        # Try to get the SME element
        sme_elements = contractor.xpath(
            "./ted:SME/text() | ./*[local-name()='SME']/text()",
            namespaces=namespaces,
        )

        # Get contractor ID - assume it's in a similar structure
        org_id_elements = contractor.xpath(
            "./ted:OFFICIALNAME/text() | ./*[local-name()='OFFICIALNAME']/text()",
            namespaces=namespaces,
        )

        if sme_elements and org_id_elements:
            sme_value = sme_elements[0].strip().lower()
            org_id = org_id_elements[0]

            # In TED format, SME is typically YES/NO - map to appropriate scale value
            scale = "sme" if sme_value == "yes" else "large"

            party = {"id": org_id, "details": {"scale": scale}}
            result["parties"].append(party)

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
