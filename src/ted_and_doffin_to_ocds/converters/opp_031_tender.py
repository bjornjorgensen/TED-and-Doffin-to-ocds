# converters/OPP_031_Tender.py

import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)

NAMESPACES = {
    "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
    "efext": "http://data.europa.eu/p27/eforms-ubl-extensions/1",
    "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
    "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    "efbc": "http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1",
}

TERM_CODE_MAPPING = {
    "cost-comp": "financialTerms",
    "other": "otherTerms",
    "publ-ser-obl": "performanceTerms",
    "soc-stand": "socialStandards",
}


def parse_contract_conditions(xml_content: str | bytes) -> dict[str, Any] | None:
    """
    Parse contract conditions information (OPP-031) from XML content.

    This mapping assumes that contract term values are consistent across all lot tenders
    for a given lot. Contact OCDS Data Support Team if values vary per lot tender.

    Gets contract terms for each lot tender and maps them to corresponding
    lots' contractTerms object based on term codes.

    Args:
        xml_content: XML content as string or bytes containing procurement data

    Returns:
        Dictionary containing lots with contract terms or None if no data found
    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")

    try:
        root = etree.fromstring(xml_content)
        result = {"tender": {"lots": []}}

        lot_tenders = root.xpath(
            "/*/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/"
            "efext:EformsExtension/efac:NoticeResult/efac:LotTender",
            namespaces=NAMESPACES,
        )

        lot_terms = {}
        for lot_tender in lot_tenders:
            lot_id = lot_tender.xpath(
                "efac:TenderLot/cbc:ID[@schemeName='Lot']/text()",
                namespaces=NAMESPACES,
            )[0]
            terms = lot_tender.xpath(
                "efac:ContractTerm[efbc:TermCode/@listName='contract-detail']/efbc:TermDescription/text()",
                namespaces=NAMESPACES,
            )
            if lot_id in lot_terms and lot_terms[lot_id] != terms:
                logger.warning(
                    "Inconsistent contract terms found for lot %s across different tenders. "
                    "Contact OCDS Data Support Team.",
                    lot_id,
                )
            lot_terms[lot_id] = terms

        for lot_tender in lot_tenders:
            try:
                lot_id = lot_tender.xpath(
                    "efac:TenderLot/cbc:ID[@schemeName='Lot']/text()",
                    namespaces=NAMESPACES,
                )[0]

                contract_terms = {}
                term_elements = lot_tender.xpath(
                    "efac:ContractTerm[efbc:TermCode/@listName='contract-detail']",
                    namespaces=NAMESPACES,
                )

                for term in term_elements:
                    term_code = term.xpath(
                        "efbc:TermCode/text()", namespaces=NAMESPACES
                    )[0]

                    # Skip all-rev-tic terms
                    if term_code == "all-rev-tic":
                        continue

                    term_description = term.xpath(
                        "efbc:TermDescription/text()",
                        namespaces=NAMESPACES,
                    )

                    if term_code == "exc-right":
                        contract_terms["hasExclusiveRights"] = True
                    elif term_description and term_code in TERM_CODE_MAPPING:
                        contract_terms[TERM_CODE_MAPPING[term_code]] = term_description[
                            0
                        ]

                if contract_terms:
                    result["tender"]["lots"].append(
                        {"id": lot_id, "contractTerms": contract_terms}
                    )

            except (IndexError, AttributeError) as e:
                logger.warning("Skipping incomplete lot tender data: %s", e)
                continue

        if result["tender"]["lots"]:
            return result

    except Exception:
        logger.exception("Error parsing contract conditions")
        return None

    return None


def merge_contract_conditions(
    release_json: dict[str, Any], conditions_data: dict[str, Any] | None
) -> None:
    """
    Merge contract conditions into the release JSON.

    Updates or creates lots with contract terms information.
    Preserves existing lot data while adding/updating contract terms.

    Args:
        release_json: The target release JSON to update
        conditions_data: The source data containing contract terms to merge

    Returns:
        None
    """
    if not conditions_data:
        logger.warning("No contract conditions data to merge")
        return

    tender = release_json.setdefault("tender", {})
    existing_lots = tender.setdefault("lots", [])

    for new_lot in conditions_data["tender"]["lots"]:
        existing_lot = next(
            (lot for lot in existing_lots if lot["id"] == new_lot["id"]),
            None,
        )
        if existing_lot:
            existing_lot.setdefault("contractTerms", {}).update(
                new_lot["contractTerms"]
            )
        else:
            existing_lots.append(new_lot)

    logger.info(
        "Merged contract conditions for %d lots",
        len(conditions_data["tender"]["lots"]),
    )
