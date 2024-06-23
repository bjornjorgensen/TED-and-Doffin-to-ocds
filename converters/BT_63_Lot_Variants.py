# converters/BT_63_Lot_Variants.py
from lxml import etree

# Mapping of variant constraint codes to policies
VARIANT_POLICY_MAPPING = {
    "required": "Required",
    "allowed": "Allowed",
    "notAllowed": "Not allowed"
}

def parse_lot_variants(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = {}

    lot_elements = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)
    for lot in lot_elements:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        variant_constraint = lot.xpath("cac:TenderingTerms/cbc:VariantConstraintCode[@listName='permission']/text()", namespaces=namespaces)
        
        if variant_constraint:
            result[lot_id] = VARIANT_POLICY_MAPPING.get(variant_constraint[0], variant_constraint[0])

    return result

def merge_lot_variants(release_json, variants_data):
    if variants_data:
        tender = release_json.setdefault("tender", {})
        lots = tender.setdefault("lots", [])

        for lot_id, variant_policy in variants_data.items():
            lot = next((lot for lot in lots if lot.get("id") == lot_id), None)
            if not lot:
                lot = {"id": lot_id}
                lots.append(lot)
            
            submission_terms = lot.setdefault("submissionTerms", {})
            submission_terms["variantPolicy"] = variant_policy

    return release_json