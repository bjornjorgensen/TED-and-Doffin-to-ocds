# converters/BT_772_Lot.py

from lxml import etree

def parse_late_tenderer_info_description(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = {}
    lot_elements = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)

    for lot in lot_elements:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        description = lot.xpath("cac:TenderingTerms/cac:TendererQualificationRequest[not(cbc:CompanyLegalFormCode)]/cac:SpecificTendererRequirement[cbc:TendererRequirementTypeCode/@listName='missing-info-submission']/cbc:Description/text()", namespaces=namespaces)
        
        if description:
            result[lot_id] = description[0]

    return result

def merge_late_tenderer_info_description(release_json, late_info_description_data):
    if not late_info_description_data:
        return release_json

    tender = release_json.setdefault("tender", {})
    lots = tender.setdefault("lots", [])

    for lot_id, description in late_info_description_data.items():
        lot = next((lot for lot in lots if lot.get("id") == lot_id), None)
        if not lot:
            lot = {"id": lot_id}
            lots.append(lot)
        
        if "submissionMethodDetails" in lot:
            lot["submissionMethodDetails"] += f" {description}"
        else:
            lot["submissionMethodDetails"] = description

    return release_json