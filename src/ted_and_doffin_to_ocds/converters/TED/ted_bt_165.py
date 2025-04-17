import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)

# BT-165: Winner Size
# TED XPaths:
# - TED_EXPORT/FORM_SECTION/F03_2014/AWARD_CONTRACT/AWARDED_CONTRACT/CONTRACTORS/CONTRACTOR/*[matches(name(),'SME')]
# - TED_EXPORT/FORM_SECTION/F13_2014/RESULTS/AWARDED_PRIZE/WINNERS/WINNER/SME
# - TED_EXPORT/FORM_SECTION/F15_2014/AWARD_CONTRACT/AWARDED_CONTRACT/CONTRACTORS/CONTRACTOR/*[matches(name(),'SME')]
# - TED_EXPORT/FORM_SECTION/F21_2014/AWARD_CONTRACT/AWARDED_CONTRACT/CONTRACTORS/CONTRACTOR/SME
# - TED_EXPORT/FORM_SECTION/F22_2014/AWARD_CONTRACT/AWARDED_CONTRACT/CONTRACTORS/CONTRACTOR/SME
# - TED_EXPORT/FORM_SECTION/F23_2014/AWARD_CONTRACT/AWARDED_CONTRACT/CONTRACTORS/CONTRACTOR/SME
# - TED_EXPORT/FORM_SECTION/F25_2014/AWARD_CONTRACT/AWARDED_CONTRACT/CONTRACTORS/CONTRACTOR/*[matches(name(),'SME')]
# OCDS Mapping: parties[].details.scale


def parse_winner_size(
    xml_content: str | bytes,
) -> dict[str, list[dict[str, Any]]] | None:
    """Parses the winner size information from TED XML content.

    Args:
        xml_content (Union[str, bytes]): The XML content to parse.

    Returns:
        Optional[Dict[str, List[Dict[str, Any]]]]: A dictionary containing party information,
        or None if no data is found.
    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")

    try:
        root = etree.fromstring(xml_content)
        result = {"parties": []}

        # Forms to check for SME information
        forms_to_check = [
            "F03_2014",
            "F13_2014",
            "F15_2014",
            "F21_2014",
            "F22_2014",
            "F23_2014",
            "F25_2014",
        ]

        for form_name in forms_to_check:
            # Different XPath patterns for different forms
            if form_name in ["F03_2014", "F15_2014", "F25_2014"]:
                contractors = root.xpath(
                    f"FORM_SECTION/{form_name}/AWARD_CONTRACT/AWARDED_CONTRACT/CONTRACTORS/CONTRACTOR",
                )
                sme_xpath = "./*[contains(name(),'SME')]/text()"
            elif form_name == "F13_2014":
                contractors = root.xpath(
                    f"FORM_SECTION/{form_name}/RESULTS/AWARDED_PRIZE/WINNERS/WINNER",
                )
                sme_xpath = "./SME/text()"
            else:  # F21_2014, F22_2014, F23_2014
                contractors = root.xpath(
                    f"FORM_SECTION/{form_name}/AWARD_CONTRACT/AWARDED_CONTRACT/CONTRACTORS/CONTRACTOR",
                )
                sme_xpath = "./SME/text()"

            for contractor in contractors:
                # Get SME information
                sme_elements = contractor.xpath(sme_xpath)

                # Get contractor name for ID
                org_name_elements = contractor.xpath("./OFFICIALNAME/text()")

                if sme_elements and org_name_elements:
                    sme_value = sme_elements[0].strip().lower()
                    org_id = org_name_elements[0].strip()

                    # Map YES/NO to sme/large
                    scale = "sme" if sme_value == "yes" else "large"

                    party = {"id": org_id, "details": {"scale": scale}}

                    # Check if party already exists to avoid duplicates
                    existing_party = next(
                        (p for p in result["parties"] if p["id"] == org_id), None
                    )

                    if not existing_party:
                        result["parties"].append(party)
                        logger.info(
                            "Found contractor %s with SME value: %s (mapped to %s scale)",
                            org_id,
                            sme_value,
                            scale,
                        )

        return result if result["parties"] else None

    except Exception:
        logger.exception("Error parsing winner size information")
        return None


def merge_winner_size(
    release_json: dict[str, Any],
    winner_size_data: dict[str, list[dict[str, Any]]] | None,
) -> None:
    """Merges the winner size data into the given release JSON.

    Args:
        release_json (Dict[str, Any]): The release JSON to merge data into.
        winner_size_data (Optional[Dict[str, List[Dict[str, Any]]]]): The winner size data to merge.

    Returns:
        None
    """
    if not winner_size_data:
        logger.info("No Winner Size data to merge")
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
