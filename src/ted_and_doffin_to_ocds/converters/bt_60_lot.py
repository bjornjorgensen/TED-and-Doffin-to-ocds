# converters/bt_60_Lot.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_eu_funds(xml_content: str | bytes) -> dict | None:
    """Parse EU funds indicator from XML content.

    This function checks if the procurement is financed by EU funds by looking for
    the EU funding program code in the XML.

    Args:
        xml_content: XML string or bytes containing procurement data

    Returns:
        Dict containing OCDS formatted data with EU party information, or None if no EU funding found.
        Format:
        {
            "parties": [{
                "id": str,
                "name": "European Union",
                "roles": ["funder"]
            }]
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

    # Check if the relevant XPath exists
    relevant_xpath = "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']/cac:TenderingTerms/cbc:FundingProgramCode[@listName='eu-funded' and text()='eu-funds']"
    if not root.xpath(relevant_xpath, namespaces=namespaces):
        logger.info("No EU funds indicator found. Skipping parse_eu_funds.")
        return None

    return {
        "parties": [
            {
                "id": "EU-1",  # Using consistent ID for EU party
                "name": "European Union",
                "roles": ["funder"],
            }
        ]
    }


def merge_eu_funds(release_json: dict, eu_funds_data: dict | None) -> None:
    """Merge EU funds data into an existing OCDS release.

    Updates the parties in the release_json with EU funder information.
    If the EU party already exists, ensures it has the funder role.

    Args:
        release_json: The OCDS release to be updated
        eu_funds_data: Data containing EU funds information to be merged.
                      Expected to have the same structure as parse_eu_funds output.

    Returns:
        None. Updates release_json in place.
    """
    if not eu_funds_data:
        logger.info("No EU funds data to merge")
        return

    parties = release_json.setdefault("parties", [])
    eu_party = next(
        (party for party in parties if party.get("name") == "European Union"),
        None,
    )

    if eu_party:
        if "funder" not in eu_party.get("roles", []):
            eu_party["roles"] = list({*eu_party.get("roles", []), "funder"})
    else:
        parties.append(eu_funds_data["parties"][0])

    logger.info("Merged EU funds data")
