# converters/BT_771_Lot.py

from lxml import etree

def parse_late_tenderer_information(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    code_to_label = {
        'late-all': "At the discretion of the buyer, all missing tenderer-related documents may be submitted later.",
        'late-none': "No documents can be submitted later.",
        'late-some': "At the discretion of the buyer, some missing tenderer-related documents may be submitted later."
    }

    result = {}
    lot_elements = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)

    for lot in lot_elements:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        code = lot.xpath("cac:TenderingTerms/cac:TendererQualificationRequest[not(cbc:CompanyLegalFormCode)]/cac:SpecificTendererRequirement[cbc:TendererRequirementTypeCode/@listName='missing-info-submission']/cbc:TendererRequirementTypeCode/text()", namespaces=namespaces)
        
        if code and code[0] in code_to_label:
            result[lot_id] = code_to_label[code[0]]

    return result

def merge_late_tenderer_information(release_json, late_info_data):
    if not late_info_data:
        return release_json

    tender = release_json.setdefault("tender", {})
    lots = tender.setdefault("lots", [])

    for lot_id, info in late_info_data.items():
        lot = next((lot for lot in lots if lot.get("id") == lot_id), None)
        if not lot:
            lot = {"id": lot_id}
            lots.append(lot)
        
        if "submissionMethodDetails" in lot:
            lot["submissionMethodDetails"] += f" {info}"
        else:
            lot["submissionMethodDetails"] = info

    return release_json