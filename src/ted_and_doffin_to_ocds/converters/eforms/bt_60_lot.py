# converters/bt_60_Lot.py

import logging
import uuid

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
            }],
            "finance": [{
                "id": str,
                "financingParty": {"id": str, "name": "European Union"},
                "relatedLots": [lot_ids],
                "description": str (optional)
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

    # Use the exact xpathAbsolute from the specification
    xpath = "/*/cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']/cac:TenderingTerms/cbc:FundingProgramCode[@listName='eu-funded']"

    lots_with_eu_funds = {}

    funding_elements = root.xpath(xpath, namespaces=namespaces)
    for element in funding_elements:
        # Check if the element text is 'eu-funds' or 'true'
        if element.text in ("eu-funds", "true"):
            # Navigate up the tree to find the ProcurementProjectLot element
            lot_element = element.xpath(
                "ancestor::cac:ProcurementProjectLot[1]", namespaces=namespaces
            )[0]
            lot_id_elements = lot_element.xpath(
                "cbc:ID[@schemeName='Lot']/text()", namespaces=namespaces
            )

            if lot_id_elements:
                lot_id = lot_id_elements[0]

                funding_program = lot_element.xpath(
                    "cac:TenderingTerms/cbc:FundingProgram/text()",
                    namespaces=namespaces,
                )

                lots_with_eu_funds[lot_id] = {
                    "id": lot_id,
                    "funding_program": funding_program[0] if funding_program else None,
                }

    funding_project_id = None
    funding_elements = root.xpath(
        "//efac:Funding/cbc:FundingProjectIdentifier/text()", namespaces=namespaces
    )
    if funding_elements:
        funding_project_id = funding_elements[0]

    if not lots_with_eu_funds:
        logger.info("No EU funds indicator found. Skipping parse_eu_funds.")
        return None

    eu_party_id = str(uuid.uuid4())
    result = {
        "parties": [
            {
                "id": eu_party_id,
                "name": "European Union",
                "roles": ["funder"],
            }
        ],
        "finance": [],
    }

    finance_obj = {
        "id": str(uuid.uuid4()),
        "financingParty": {"id": eu_party_id, "name": "European Union"},
        "relatedLots": list(lots_with_eu_funds.keys()),
    }

    if funding_project_id:
        finance_obj["description"] = funding_project_id

    result["finance"].append(finance_obj)
    return result


def merge_eu_funds(release_json: dict, eu_funds_data: dict | None) -> None:
    """Merge EU funds data into an existing OCDS release.

    Updates the parties in the release_json with EU funder information.
    If the EU party already exists, ensures it has the funder role.
    Adds finance information to planning.budget.finance.

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
        eu_party = eu_funds_data["parties"][0]

    if "planning" not in release_json:
        release_json["planning"] = {}
    if "budget" not in release_json["planning"]:
        release_json["planning"]["budget"] = {}
    if "finance" not in release_json["planning"]["budget"]:
        release_json["planning"]["budget"]["finance"] = []

    for finance_obj in eu_funds_data.get("finance", []):
        finance_obj["financingParty"]["id"] = eu_party["id"]
        release_json["planning"]["budget"]["finance"].append(finance_obj)

    logger.info("Merged EU funds data")
