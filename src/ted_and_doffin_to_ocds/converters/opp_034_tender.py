# converters/OPP_034_Tender.py

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


def parse_penalties_and_rewards(xml_content: str | bytes) -> dict[str, Any] | None:
    """
    Parse penalties and rewards information (OPP-034) from XML content.

    This mapping assumes that rewards and penalties descriptions are consistent across all lot tenders
    for a given lot. Contact OCDS Data Support Team if values vary per lot tender.

    Gets rewards and penalties descriptions from each lot tender and maps them
    to corresponding lot's contractTerms.rewardsAndPenalties field.

    Args:
        xml_content: XML content as string or bytes containing procurement data

    Returns:
        Dictionary containing lots with penalties and rewards or None if no data found
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
            try:
                lot_id = lot_tender.xpath(
                    "efac:TenderLot/cbc:ID[@schemeName='Lot']/text()",
                    namespaces=NAMESPACES,
                )[0]

                term_description = lot_tender.xpath(
                    "efac:ContractTerm[efbc:TermCode/@listName='rewards-penalties']/"
                    "efbc:TermDescription/text()",
                    namespaces=NAMESPACES,
                )

                if term_description:
                    if lot_id in lot_terms and lot_terms[lot_id] != term_description[0]:
                        logger.warning(
                            "Inconsistent rewards and penalties found for lot %s across different tenders. "
                            "Contact OCDS Data Support Team.",
                            lot_id,
                        )
                    lot_terms[lot_id] = term_description[0]

                    result["tender"]["lots"].append(
                        {
                            "id": lot_id,
                            "contractTerms": {
                                "rewardsAndPenalties": term_description[0]
                            },
                        }
                    )

            except (IndexError, AttributeError) as e:
                logger.warning("Skipping incomplete lot tender data: %s", e)
                continue

        if result["tender"]["lots"]:
            return result

    except Exception:
        logger.exception("Error parsing penalties and rewards")
        return None

    return None


def merge_penalties_and_rewards(
    release_json: dict[str, Any], penalties_data: dict[str, Any] | None
) -> None:
    """
    Merge penalties and rewards information into the release JSON.

    Updates or creates lots with rewards and penalties descriptions.
    Preserves existing lot data while adding/updating rewards info.

    Args:
        release_json: The target release JSON to update
        penalties_data: The source data containing penalties info to merge

    Returns:
        None
    """
    if not penalties_data:
        logger.warning("No penalties and rewards data to merge")
        return

    tender = release_json.setdefault("tender", {})
    existing_lots = tender.setdefault("lots", [])

    for new_lot in penalties_data["tender"]["lots"]:
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
        "Merged penalties and rewards for %d lots",
        len(penalties_data["tender"]["lots"]),
    )
