# converters/BT_65_Lot_Subcontracting_Obligation.py
from lxml import etree

SUBCONTRACTING_OBLIGATION_MAPPING = {
    "none": "No subcontracting obligation applies.",
    "subc-chng": "The contractor must indicate any change of subcontractors during the execution of the contract.",
    "subc-min": "The contractor must subcontract a minimum percentage of the contract using the procedure set out in Title III of Directive 2009/81/EC.",
    "subc-oblig-2009-81": "The buyer may oblige the contractor to award all or certain subcontracts through the procedure set out in Title III of Directive 2009/81/EC."
}

def parse_subcontracting_obligation(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = {}

    lot_elements = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)
    for lot in lot_elements:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        obligation_code = lot.xpath(".//cac:AllowedSubcontractTerms[cbc:SubcontractingConditionsCode/@listName='subcontracting-obligation']/cbc:SubcontractingConditionsCode/text()", namespaces=namespaces)
        
        if obligation_code and obligation_code[0] != "none":
            result[lot_id] = SUBCONTRACTING_OBLIGATION_MAPPING.get(obligation_code[0], "Unknown subcontracting obligation")

    return result

def merge_subcontracting_obligation(release_json, obligation_data):
    if obligation_data:
        tender = release_json.setdefault("tender", {})
        lots = tender.setdefault("lots", [])

        for lot_id, description in obligation_data.items():
            lot = next((lot for lot in lots if lot.get("id") == lot_id), None)
            if not lot:
                lot = {"id": lot_id}
                lots.append(lot)
            
            subcontracting_terms = lot.setdefault("subcontractingTerms", {})
            subcontracting_terms["description"] = description

    return release_json