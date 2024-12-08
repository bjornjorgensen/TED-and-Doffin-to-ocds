# converters/bt_5010_Lot.py

import logging
from typing import Any

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


def parse_eu_funds_financing_identifier(
    xml_content: str | bytes,
) -> dict[str, Any] | None:
    """Parse EU Funds Financing Identifier (BT-5010) from XML content."""
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")

    try:
        root = etree.fromstring(xml_content)

        result = {"parties": [], "planning": {"budget": {"finance": []}}}

        # Get all lots with financing identifiers using exact XPath
        lots = root.xpath(
            "/*/cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']",
            namespaces=NAMESPACES,
        )

        found_financing = False
        for lot in lots:
            lot_id = lot.xpath("cbc:ID/text()", namespaces=NAMESPACES)[0]

            # Get financing identifiers using exact BT-5010 path
            financing_ids = lot.xpath(
                "cac:TenderingTerms/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/"
                "efext:EformsExtension/efac:Funding/efbc:FinancingIdentifier/text()",
                namespaces=NAMESPACES,
            )

            for financing_id in financing_ids:
                found_financing = True
                result["planning"]["budget"]["finance"].append(
                    {
                        "id": financing_id,
                        "financingParty": {
                            "name": "European Union"  # ID will be added during merge
                        },
                        "relatedLots": [lot_id],
                    }
                )

        if found_financing:
            # Add EU party if financing exists
            result["parties"].append({"name": "European Union", "roles": ["funder"]})
            return result

    except Exception:
        logger.exception("Error parsing EU funds financing identifier")
        return None
    else:
        return None


def merge_eu_funds_financing_identifier(
    release_json: dict[str, Any],
    eu_funds_data: dict[str, Any] | None,
) -> None:
    """Merge EU Funds Financing Identifier data into the release JSON."""
    if not eu_funds_data:
        logger.debug("No EU Funds Financing Identifier data to merge")
        return

    # Handle EU party
    parties = release_json.setdefault("parties", [])
    eu_party = next(
        (party for party in parties if party.get("name") == "European Union"), None
    )

    if eu_party:
        if "funder" not in eu_party.get("roles", []):
            eu_party.setdefault("roles", []).append("funder")
    else:
        eu_party = {
            "id": str(len(parties) + 1),
            "name": "European Union",
            "roles": ["funder"],
        }
        parties.append(eu_party)

    # Handle finance information
    planning = release_json.setdefault("planning", {})
    budget = planning.setdefault("budget", {})
    existing_finance = budget.setdefault("finance", [])

    for new_finance in eu_funds_data["planning"]["budget"]["finance"]:
        existing_item = next(
            (item for item in existing_finance if item["id"] == new_finance["id"]), None
        )

        if existing_item:
            # Update existing finance entry
            existing_item["financingParty"] = {
                "id": eu_party["id"],
                "name": "European Union",
            }
            # Merge relatedLots arrays
            existing_lots = existing_item.get("relatedLots", [])
            existing_lots.extend(new_finance["relatedLots"])
            existing_item["relatedLots"] = list(set(existing_lots))
        else:
            # Add new finance entry with proper party reference
            new_finance["financingParty"]["id"] = eu_party["id"]
            existing_finance.append(new_finance)

    logger.info(
        "Merged EU Funds Financing data for %d finance items",
        len(eu_funds_data["planning"]["budget"]["finance"]),
    )
