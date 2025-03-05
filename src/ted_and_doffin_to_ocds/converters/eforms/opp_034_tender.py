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


def _process_lot_results(root, lot_data) -> None:
    """Process lot results and populate lot_data dictionary."""
    lot_results = root.xpath(
        "/*/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/"
        "efext:EformsExtension/efac:NoticeResult/efac:LotResult",
        namespaces=NAMESPACES,
    )

    for lot_result in lot_results:
        try:
            tender_id = lot_result.xpath(
                "efac:LotTender/cbc:ID[@schemeName='tender']/text()",
                namespaces=NAMESPACES,
            )[0]

            lot_id = lot_result.xpath(
                "efac:TenderLot/cbc:ID[@schemeName='Lot']/text()",
                namespaces=NAMESPACES,
            )[0]

            if lot_id not in lot_data:
                lot_data[lot_id] = {
                    "id": lot_id,
                    "contractTerms": {},
                    "penaltiesAndRewards": {"penalties": [], "rewards": []},
                    "tenders": set(),
                }

            lot_data[lot_id]["tenders"].add(tender_id)

        except (IndexError, AttributeError) as e:
            logger.warning("Skipping incomplete lot result data: %s", e)
            continue


def _process_term_descriptions(lot_tender, associated_lots, lot_data) -> None:
    """Process term descriptions from lot tender."""
    term_descriptions = lot_tender.xpath(
        "efac:ContractTerm[efbc:TermCode/@listName='rewards-penalties']/"
        "efbc:TermDescription",
        namespaces=NAMESPACES,
    )

    if not term_descriptions:
        return

    # If there's only one description or no language attribute, use simple string
    if len(term_descriptions) == 1 or not term_descriptions[0].get("languageID"):
        description_value = term_descriptions[0].text
    else:
        # Create a structured representation for multilingual content
        description_value = {}
        for desc in term_descriptions:
            lang_id = desc.get("languageID")
            if lang_id:
                description_value[lang_id] = desc.text

    for lot_id in associated_lots:
        if (
            "rewardsAndPenalties" in lot_data[lot_id]["contractTerms"]
            and lot_data[lot_id]["contractTerms"]["rewardsAndPenalties"]
            != description_value
        ):
            logger.warning(
                "Inconsistent rewards and penalties found for lot %s across different tenders. "
                "Contact OCDS Data Support Team.",
                lot_id,
            )
        lot_data[lot_id]["contractTerms"]["rewardsAndPenalties"] = description_value


def _process_performance_requirements(lot_tender, associated_lots, lot_data) -> None:
    """Process financial performance requirements from lot tender."""
    performance_requirements = lot_tender.xpath(
        "efac:ContractTerm/efac:FinancialPerformanceRequirement",
        namespaces=NAMESPACES,
    )

    for req in performance_requirements:
        type_code = req.xpath(
            "efbc:FinancialPerformanceTypeCode/text()",
            namespaces=NAMESPACES,
        )
        if not type_code:
            continue

        type_code = type_code[0]

        description = req.xpath(
            "efbc:FinancialPerformanceDescription/text()",
            namespaces=NAMESPACES,
        )
        if not description:
            continue

        description = description[0]

        for lot_id in associated_lots:
            if (
                type_code == "penalty"
                and description
                not in lot_data[lot_id]["penaltiesAndRewards"]["penalties"]
            ):
                lot_data[lot_id]["penaltiesAndRewards"]["penalties"].append(description)
            elif (
                type_code == "reward"
                and description
                not in lot_data[lot_id]["penaltiesAndRewards"]["rewards"]
            ):
                lot_data[lot_id]["penaltiesAndRewards"]["rewards"].append(description)


def _process_lot_tenders(root, lot_data) -> None:
    """Process lot tenders and update lot_data dictionary."""
    lot_tenders = root.xpath(
        "/*/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/"
        "efext:EformsExtension/efac:NoticeResult/efac:LotTender",
        namespaces=NAMESPACES,
    )

    for lot_tender in lot_tenders:
        try:
            tender_id = lot_tender.xpath(
                "cbc:ID[@schemeName='tender']/text()",
                namespaces=NAMESPACES,
            )

            if not tender_id:
                continue
            tender_id = tender_id[0]

            # Find associated lots for this tender
            associated_lots = [
                lot_id
                for lot_id, data in lot_data.items()
                if tender_id in data["tenders"]
            ]

            if not associated_lots:
                continue

            # Process term descriptions
            _process_term_descriptions(lot_tender, associated_lots, lot_data)

            # Process performance requirements
            _process_performance_requirements(lot_tender, associated_lots, lot_data)

        except (IndexError, AttributeError) as e:
            logger.warning("Skipping incomplete lot tender data: %s", e)
            continue


def parse_penalties_and_rewards(xml_content: str | bytes) -> dict[str, Any] | None:
    """Parse penalties and rewards information (OPP-034) from XML content.

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

        # Create a mapping to collect data per lot
        lot_data = {}

        # Process lot results
        _process_lot_results(root, lot_data)

        # Process lot tenders
        _process_lot_tenders(root, lot_data)

        # Convert the lot data to the expected format
        for data in lot_data.values():
            if (
                "rewardsAndPenalties" in data["contractTerms"]
                or data["penaltiesAndRewards"]["penalties"]
                or data["penaltiesAndRewards"]["rewards"]
            ):
                # Remove the temporary tenders set before adding to result
                data.pop("tenders")
                result["tender"]["lots"].append(data)

        if result["tender"]["lots"]:
            return result

    except Exception:
        logger.exception("Error parsing penalties and rewards")
        return None

    return None


def merge_penalties_and_rewards(
    release_json: dict[str, Any], penalties_data: dict[str, Any] | None
) -> None:
    """Merge penalties and rewards information into the release JSON.

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
            # Update contractTerms
            existing_lot.setdefault("contractTerms", {}).update(
                new_lot.get("contractTerms", {})
            )
            # Update penaltiesAndRewards
            if "penaltiesAndRewards" in new_lot:
                existing_lot["penaltiesAndRewards"] = new_lot["penaltiesAndRewards"]
        else:
            existing_lots.append(new_lot)

    logger.info(
        "Merged penalties and rewards for %d lots",
        len(penalties_data["tender"]["lots"]),
    )
