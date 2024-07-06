# converters/BT_762_notice.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)

def parse_change_reason_description(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
        'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
        'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
        'efbc': 'http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1'
    }

    result = {"tender": {"amendments": []}}

    change_reasons = root.xpath("//efac:Changes/efac:ChangeReason", namespaces=namespaces)
    
    for change_reason in change_reasons:
        reason_description = change_reason.xpath("efbc:ReasonDescription/text()", namespaces=namespaces)
        if reason_description:
            amendment = {
                "rationale": reason_description[0]
            }
            result["tender"]["amendments"].append(amendment)

    return result if result["tender"]["amendments"] else None

def merge_change_reason_description(release_json, change_reason_description_data):
    if not change_reason_description_data:
        logger.warning("No Change Reason Description data to merge")
        return

    existing_amendments = release_json.setdefault("tender", {}).setdefault("amendments", [])
    new_amendments = change_reason_description_data["tender"]["amendments"]

    if len(existing_amendments) != len(new_amendments):
        logger.warning(f"Mismatch in number of amendments: {len(existing_amendments)} existing vs {len(new_amendments)} new")

    # Update existing amendments or add new ones
    for i, new_amendment in enumerate(new_amendments):
        if i < len(existing_amendments):
            existing_amendments[i].update(new_amendment)
        else:
            existing_amendments.append(new_amendment)

    logger.info(f"Merged Change Reason Description data for {len(new_amendments)} amendments")