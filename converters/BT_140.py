from lxml import etree

REASON_CODE_DESCRIPTIONS = {
    "cancel": "Notice cancelled",
    "cancel-intent": "Cancellation intention",
    "cor-buy": "Buyer correction",
    "cor-esen": "eSender correction",
    "cor-pub": "Publisher correction",
    "info-release": "Information now available",
    "susp-review": "Procedure suspended due to a complaint, appeal or any other action for review",
    "update-add": "Information updated"
}

def parse_change_reason_code_and_description(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
        'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
        'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
        'efbc': 'http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = {"tender": {"amendments": []}, "awards": []}
    changes = root.xpath("//efac:Changes", namespaces=namespaces)
    
    for changes_group in changes:
        reason_code = changes_group.xpath("efac:ChangeReason/cbc:ReasonCode/text()", namespaces=namespaces)[0]
        change_elements = changes_group.xpath("efac:Change", namespaces=namespaces)

        for i, change in enumerate(change_elements, start=1):
            section = change.xpath("efbc:ChangedSectionIdentifier/text()", namespaces=namespaces)[0]
            description = change.xpath("efbc:ChangeDescription/text()", namespaces=namespaces)
            
            amendment = {
                "id": str(i),
                "rationaleClassifications": [{
                    "id": reason_code,
                    "description": REASON_CODE_DESCRIPTIONS.get(reason_code, "Unknown reason"),
                    "scheme": "eu-change-corrig-justification"
                }]
            }
            
            if description:
                amendment["description"] = description[0]

            if section.startswith("RES-"):
                award_id = section
                award = next((a for a in result["awards"] if a["id"] == award_id), None)
                if not award:
                    award = {"id": award_id, "amendments": [], "relatedLots": []}
                    result["awards"].append(award)
                award["amendments"].append(amendment)
            elif section.startswith("LOT-"):
                amendment["relatedLots"] = [section]
                result["tender"]["amendments"].append(amendment)
            elif section.startswith("GLO-"):
                amendment["relatedLotGroups"] = [section]
                result["tender"]["amendments"].append(amendment)

    return result if result["tender"]["amendments"] or result["awards"] else None