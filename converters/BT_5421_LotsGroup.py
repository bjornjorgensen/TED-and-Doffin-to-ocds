# converters/BT_5421_LotsGroup.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)

def parse_award_criterion_number_weight_lots_group(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
        'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
        'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
        'efbc': 'http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1'
    }

    result = {"tender": {"lotGroups": []}}

    number_weight_mapping = {
        'dec-exa': 'decimalExact',
        'dec-mid': 'decimalRangeMiddle',
        'ord-imp': 'order',
        'per-exa': 'percentageExact',
        'per-mid': 'percentageRangeMiddle',
        'poi-exa': 'pointsExact',
        'poi-mid': 'pointsRangeMiddle'
    }

    lots_groups = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='LotsGroup']", namespaces=namespaces)
    
    for lot_group in lots_groups:
        lot_group_id = lot_group.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        
        award_criteria = lot_group.xpath(".//cac:AwardingTerms/cac:AwardingCriterion/cac:SubordinateAwardingCriterion", namespaces=namespaces)
        
        lot_group_data = {
            "id": lot_group_id,
            "awardCriteria": {
                "criteria": []
            }
        }

        for criterion in award_criteria:
            criterion_data = {"numbers": []}
            
            number_weights = criterion.xpath(".//efac:AwardCriterionParameter[efbc:ParameterCode/@listName='number-weight']/efbc:ParameterCode/text()", namespaces=namespaces)
            
            for weight in number_weights:
                if weight in number_weight_mapping:
                    criterion_data["numbers"].append({"weight": number_weight_mapping[weight]})
            
            if criterion_data["numbers"]:
                lot_group_data["awardCriteria"]["criteria"].append(criterion_data)

        if lot_group_data["awardCriteria"]["criteria"]:
            result["tender"]["lotGroups"].append(lot_group_data)

    return result if result["tender"]["lotGroups"] else None

def merge_award_criterion_number_weight_lots_group(release_json, award_criterion_number_weight_data):
    if not award_criterion_number_weight_data:
        logger.warning("No Award Criterion Number Weight data to merge")
        return

    tender = release_json.setdefault("tender", {})
    existing_lot_groups = tender.setdefault("lotGroups", [])
    
    for new_lot_group in award_criterion_number_weight_data["tender"]["lotGroups"]:
        existing_lot_group = next((lg for lg in existing_lot_groups if lg["id"] == new_lot_group["id"]), None)
        
        if existing_lot_group:
            existing_criteria = existing_lot_group.setdefault("awardCriteria", {}).setdefault("criteria", [])
            
            for new_criterion in new_lot_group["awardCriteria"]["criteria"]:
                existing_criterion = next((c for c in existing_criteria if c.get("id") == new_criterion.get("id")), None)
                
                if existing_criterion:
                    existing_numbers = existing_criterion.setdefault("numbers", [])
                    for new_number in new_criterion["numbers"]:
                        existing_number = next((n for n in existing_numbers if n.get("id") == new_number.get("id")), None)
                        if existing_number:
                            existing_number.update(new_number)
                        else:
                            existing_numbers.append(new_number)
                else:
                    existing_criteria.append(new_criterion)
        else:
            existing_lot_groups.append(new_lot_group)

    logger.info(f"Merged Award Criterion Number Weight data for {len(award_criterion_number_weight_data['tender']['lotGroups'])} lot groups")