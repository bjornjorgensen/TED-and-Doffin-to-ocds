import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_exclusion_grounds_sources(
    xml_content: str | bytes,
) -> dict[str, dict[str, dict[str, list[str]]]] | None:
    """Parse XML content to extract exclusion grounds sources (BT-806).

    This function extracts information about where the exclusion grounds
    are defined (e.g. procurement documents or ESPD).

    Args:
        xml_content: XML string or bytes containing the procurement data

    Returns:
        A dictionary containing tender exclusion grounds sources if found,
        otherwise None. Structure:
        {
            "tender": {
                "exclusionGrounds": {
                    "sources": [str, ...]
                }
            }
        }

    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")

    root: etree._Element = etree.fromstring(xml_content)
    namespaces = {
        "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    }

    sources: list = root.xpath(
        "//cac:TenderingTerms/cac:TendererQualificationRequest"
        "/cac:SpecificTendererRequirement"
        "/cbc:TendererRequirementTypeCode[@listName='exclusion-grounds-source']/text()",
        namespaces=namespaces,
    )

    if not sources:
        return None

    return {
        "tender": {
            "exclusionGrounds": {
                "sources": sources,
            }
        }
    }


def merge_exclusion_grounds_sources(
    release_json: dict,
    exclusion_grounds_sources: dict[str, dict[str, dict[str, list[str]]]] | None = None,
) -> None:
    """Merge exclusion grounds sources into the release JSON.

    Args:
        release_json: The target release JSON to update
        exclusion_grounds_sources: Source data containing exclusion grounds sources.
            If None, function returns without making changes.

    """
    if not exclusion_grounds_sources:
        logger.warning("No exclusion grounds sources to merge")
        return

    tender = release_json.setdefault("tender", {})
    exclusion_grounds = tender.setdefault("exclusionGrounds", {})
    existing_sources = exclusion_grounds.setdefault("sources", [])

    new_sources = exclusion_grounds_sources["tender"]["exclusionGrounds"]["sources"]
    existing_sources.extend(
        source for source in new_sources if source not in existing_sources
    )

    logger.info("Merged %d exclusion grounds sources", len(new_sources))
