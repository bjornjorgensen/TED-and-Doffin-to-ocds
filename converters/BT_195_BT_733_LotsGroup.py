# converters/BT_195_BT_733_LotsGroup.py

from lxml import etree

def parse_unpublished_award_criteria_order_justification_lotsgroup_bt733(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
    'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
    'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
    'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
    'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
    'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
    'efbc': 'http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1'
}

    withheld_info = []

    xpath = "/*/cac:ProcurementProjectLot[cbc:ID/@schemeName='LotsGroup']/cac:TenderingTerms/cac:AwardingTerms/cac:AwardingCriterion/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='awa-cri-ord']"
    
    for element in root.xpath(xpath, namespaces=namespaces):
        field_code = element.xpath("efbc:FieldIdentifierCode/text()", namespaces=namespaces)[0]
        lots_group_id = element.xpath("ancestor::cac:ProcurementProjectLot/cbc:ID[@schemeName='LotsGroup']/text()", namespaces=namespaces)[0]
        
        withheld_info.append({
            "id": f"{field_code}-{lots_group_id}",
            "field": field_code,
            "name": "Award Criteria Order Justification"
        })

    return {"withheldInformation": withheld_info} if withheld_info else None

def merge_unpublished_award_criteria_order_justification_lotsgroup_bt733(release_json, withheld_info_data):
    if not withheld_info_data:
        return

    release_json.setdefault("withheldInformation", []).extend(withheld_info_data["withheldInformation"])