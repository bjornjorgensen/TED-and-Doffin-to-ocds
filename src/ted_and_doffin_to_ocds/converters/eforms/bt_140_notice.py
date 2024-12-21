# converters/bt_140_notice.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)

# Change reason code lookup table
REASON_CODE_MAPPING = {
    "cancel": "notice cancelled",
    "cancel-intent": "Cancellation intention",
    "cor-buy": "buyer correction",
    "cor-esen": "eSender correction",
    "cor-pub": "Publisher correction",
    "info-release": "Information now available",
    "susp-review": "procedure suspended due to a complaint, appeal or any other action for review",
    "update-add": "Information updated",
}


def parse_change_reason_code(xml_content: str | bytes) -> dict | None:
    """Parse the change reason code from XML data.

    Args:
        xml_content (Union[str, bytes]): The XML content containing change information

    Returns:
        Optional[Dict]: Dictionary containing tender information, or None if no data found
        The structure follows the format shown in the example output

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

    result = {"tender": {"amendments": []}, "awards": []}
    amendment_id = 1

    changes_elements = root.xpath("//efac:Changes", namespaces=namespaces)
    for changes_element in changes_elements:
        reason_code = changes_element.xpath(
            "efac:ChangeReason/cbc:ReasonCode[@listName='change-corrig-justification']/text()",
            namespaces=namespaces,
        )
        if not reason_code:
            continue

        reason_code = reason_code[0]
        classification = {
            "scheme": "eu-change-corrig-justification",
            "id": reason_code,
            "description": REASON_CODE_MAPPING.get(reason_code, "Unknown"),
        }

        for change in changes_element.xpath("efac:Change", namespaces=namespaces):
            section_id = change.xpath(
                "efbc:ChangedSectionIdentifier/text()", namespaces=namespaces
            )
            description = change.xpath(
                "efbc:ChangeDescription/text()", namespaces=namespaces
            )

            if not section_id:
                continue

            section_id = section_id[0]
            amendment = {
                "id": str(amendment_id),
                "rationaleClassifications": [classification],
            }
            if description:
                amendment["description"] = description[0]

            # Handle different section types
            if section_id.startswith("RES-"):
                award = next(
                    (a for a in result["awards"] if a["id"] == section_id),
                    {"id": section_id, "amendments": []},
                )
                if award not in result["awards"]:
                    result["awards"].append(award)
                award["amendments"].append(amendment)
            else:
                if section_id.startswith("LOT-"):
                    amendment["relatedLots"] = [section_id]
                elif section_id.startswith("GLO-"):
                    amendment["relatedLotGroups"] = [section_id]
                result["tender"]["amendments"].append(amendment)

            amendment_id += 1

    return result if result["tender"]["amendments"] or result["awards"] else None


def merge_change_reason_code(
    release_json: dict, change_reason_data: dict | None
) -> None:
    """Merge change reason code data into the release JSON.

    Args:
        release_json (Dict): The target release JSON to merge data into
        change_reason_data (Optional[Dict]): The source data containing changes
            to be merged. If None, function returns without making changes.

    """
    if not change_reason_data:
        logger.warning("No change reason code data to merge")
        return

    tender_amendments = release_json.setdefault("tender", {}).setdefault(
        "amendments",
        [],
    )
    tender_amendments.extend(change_reason_data["tender"]["amendments"])

    existing_awards = release_json.setdefault("awards", [])
    for new_award in change_reason_data["awards"]:
        existing_award = next(
            (a for a in existing_awards if a["id"] == new_award["id"]),
            None,
        )
        if existing_award:
            existing_award.setdefault("amendments", []).extend(new_award["amendments"])
        else:
            existing_awards.append(new_award)

    logger.info(
        "Merged change reason code and description data for %d tender amendments and %d awards",
        len(change_reason_data["tender"]["amendments"]),
        len(change_reason_data["awards"]),
    )
