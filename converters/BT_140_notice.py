# converters/BT_140_notice.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)

def parse_change_reason_code(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
    'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
    'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
    'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
    'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
    'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
    'efbc': 'http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1'
}

    result = {"tender": {"amendments": []}, "awards": []}

    changes = root.xpath("//efac:Changes", namespaces=namespaces)
    
    reason_code_mapping = {
        'cancel': 'Notice cancelled',
        'cancel-intent': 'Cancellation intention',
        'cor-buy': 'Buyer correction',
        'cor-esen': 'eSender correction',
        'cor-pub': 'Publisher correction',
        'info-release': 'Information now available',
        'susp-review': 'Procedure suspended due to a complaint, appeal or any other action for review',
        'update-add': 'Information updated'
    }

    for changes_element in changes:
        reason_code = changes_element.xpath("efac:ChangeReason/cbc:ReasonCode[@listName='change-corrig-justification']/text()", namespaces=namespaces)
        if not reason_code:
            continue

        reason_code = reason_code[0]
        change_elements = changes_element.xpath("efac:Change", namespaces=namespaces)

        for i, change in enumerate(change_elements, start=1):
            section_identifier = change.xpath("efbc:ChangedSectionIdentifier/text()", namespaces=namespaces)
            change_description = change.xpath("efbc:ChangeDescription/text()", namespaces=namespaces)
            
            if not section_identifier:
                continue

            section_identifier = section_identifier[0]
            amendment = {
                "id": str(i),
                "rationaleClassifications": [
                    {
                        "id": reason_code,
                        "description": reason_code_mapping.get(reason_code, "Unknown"),
                        "scheme": "eu-change-corrig-justification"
                    }
                ]
            }

            if change_description:
                amendment["description"] = change_description[0]

            if section_identifier.startswith("RES-"):
                award = next((a for a in result["awards"] if a["id"] == section_identifier), None)
                if not award:
                    award = {"id": section_identifier, "amendments": []}
                    result["awards"].append(award)
                award["amendments"].append(amendment)
            elif section_identifier.startswith("LOT-"):
                amendment["relatedLots"] = [section_identifier]
                result["tender"]["amendments"].append(amendment)
            elif section_identifier.startswith("GLO-"):
                amendment["relatedLotGroups"] = [section_identifier]
                result["tender"]["amendments"].append(amendment)

    return result if (result["tender"]["amendments"] or any(award.get("amendments") for award in result["awards"])) else None

def merge_change_reason_code(release_json, change_reason_code_data):
    if not change_reason_code_data:
        logger.warning("No change reason code data to merge")
        return

    tender_amendments = release_json.setdefault("tender", {}).setdefault("amendments", [])
    tender_amendments.extend(change_reason_code_data["tender"]["amendments"])

    existing_awards = release_json.setdefault("awards", [])
    for new_award in change_reason_code_data["awards"]:
        existing_award = next((a for a in existing_awards if a["id"] == new_award["id"]), None)
        if existing_award:
            existing_award.setdefault("amendments", []).extend(new_award["amendments"])
        else:
            existing_awards.append(new_award)

    logger.info(f"Merged change reason code and description data for {len(change_reason_code_data['tender']['amendments'])} tender amendments and {len(change_reason_code_data['awards'])} awards")