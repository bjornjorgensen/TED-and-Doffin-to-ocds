# converters/bt_5011_Contract.py

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


def parse_contract_eu_funds_financing_identifier(
    xml_content: str | bytes,
) -> dict[str, Any] | None:
    """Parse contract EU funds financing identifier (BT-5011) from XML content."""
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")

    try:
        root = etree.fromstring(xml_content)
        result = {"parties": [], "contracts": []}

        # Get settled contracts using exact BT-5011 path
        settled_contracts = root.xpath(
            "/*/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/"
            "efac:NoticeResult/efac:SettledContract",
            namespaces=NAMESPACES,
        )

        found_financing = False
        for contract in settled_contracts:
            try:
                contract_id = contract.xpath(
                    "cbc:ID[@schemeName='contract']/text()", namespaces=NAMESPACES
                )[0]

                funding_elements = contract.xpath(
                    "efac:Funding/efbc:FinancingIdentifier/text()",
                    namespaces=NAMESPACES,
                )

                contract_finance = []
                for financing_id in funding_elements:
                    found_financing = True
                    finance_item = {
                        "id": financing_id,
                        "financingParty": {
                            "name": "European Union"  # ID will be added during merge
                        },
                    }
                    contract_finance.append(finance_item)

                if contract_finance:
                    result["contracts"].append(
                        {"id": contract_id, "finance": contract_finance}
                    )

            except (IndexError, AttributeError) as e:
                logger.warning("Skipping incomplete contract data: %s", e)
                continue

        if found_financing:
            result["parties"].append({"name": "European Union", "roles": ["funder"]})
            return result

    except Exception:
        logger.exception("Error parsing contract EU funds financing identifier")
        return None
    else:
        return None


def merge_contract_eu_funds_financing_identifier(
    release_json: dict[str, Any], eu_funds_data: dict[str, Any] | None
) -> None:
    """Merge contract EU funds financing identifier data into the release JSON."""
    if not eu_funds_data:
        logger.debug("No Contract EU Funds Financing data to merge")
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

    # Handle finance information in contracts
    existing_contracts = release_json.setdefault("contracts", [])

    for new_contract in eu_funds_data["contracts"]:
        existing_contract = next(
            (c for c in existing_contracts if c["id"] == new_contract["id"]), None
        )

        if existing_contract:
            existing_finance = existing_contract.setdefault("finance", [])
            for new_finance in new_contract["finance"]:
                existing_item = next(
                    (f for f in existing_finance if f["id"] == new_finance["id"]), None
                )
                if existing_item:
                    existing_item["financingParty"] = {
                        "id": eu_party["id"],
                        "name": "European Union",
                    }
                else:
                    new_finance["financingParty"]["id"] = eu_party["id"]
                    existing_finance.append(new_finance)
        else:
            # Add financing party ID to all finance items
            for finance_item in new_contract["finance"]:
                finance_item["financingParty"]["id"] = eu_party["id"]
            existing_contracts.append(new_contract)

    logger.info(
        "Merged Contract EU Funds Financing data for %d contracts",
        len(eu_funds_data["contracts"]),
    )
