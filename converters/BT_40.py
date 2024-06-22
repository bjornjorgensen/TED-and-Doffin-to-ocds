# converters/BT_40.py
from lxml import etree

def parse_selection_criteria_second_stage(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
        'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
        'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
        'efbc': 'http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1'
    }
    
    result = {"tender": {"lots": []}}

    lot_elements = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)
    for lot_element in lot_elements:
        lot_id = lot_element.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        
        selection_criteria_elements = lot_element.xpath(
            "cac:TenderingTerms/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:SelectionCriteria",
            namespaces=namespaces
        )
        
        criteria = []
        for selection_criteria in selection_criteria_elements:
            usage = selection_criteria.xpath("cbc:CalculationExpressionCode[@listName='usage']/text()", namespaces=namespaces)
            if usage and usage[0] == "used":
                second_stage_indicator = selection_criteria.xpath("efbc:SecondStageIndicator/text()", namespaces=namespaces)
                if second_stage_indicator:
                    criteria.append({
                        "forReduction": second_stage_indicator[0].lower() == "true"
                    })
        
        if criteria:
            lot = {
                "id": lot_id,
                "selectionCriteria": {
                    "criteria": criteria
                }
            }
            result["tender"]["lots"].append(lot)
    
    return result if result["tender"]["lots"] else None

def merge_selection_criteria_second_stage(release_json, selection_criteria_data):
    if selection_criteria_data and "tender" in selection_criteria_data and "lots" in selection_criteria_data["tender"]:
        tender = release_json.setdefault("tender", {})
        existing_lots = tender.setdefault("lots", [])
        
        for new_lot in selection_criteria_data["tender"]["lots"]:
            existing_lot = next((lot for lot in existing_lots if lot["id"] == new_lot["id"]), None)
            if existing_lot:
                existing_criteria = existing_lot.setdefault("selectionCriteria", {}).setdefault("criteria", [])
                for new_criterion in new_lot["selectionCriteria"]["criteria"]:
                    # Assuming we want to update existing criteria or add new ones
                    existing_criterion = next((c for c in existing_criteria if "forReduction" in c), None)
                    if existing_criterion:
                        existing_criterion["forReduction"] = new_criterion["forReduction"]
                    else:
                        existing_criteria.append(new_criterion)
            else:
                existing_lots.append(new_lot)
