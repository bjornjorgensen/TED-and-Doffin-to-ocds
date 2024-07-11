# converters/BT_196_BT_540_LotsGroup.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)

def parse_unpublished_justification_description_lotsgroup_bt540(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
        'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
        'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
        'efbc': 'http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1'
    }

    xpath = "/*/cac:ProcurementProjectLot[cbc:ID/@schemeName='LotsGroup']/cac:TenderingTerms/cac:AwardingTerms/cac:AwardingCriterion/cac:SubordinateAwardingCriterion/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='awa-cri-des']/efbc:ReasonDescription"
    
    results = []
    reason_descriptions = root.xpath(xpath, namespaces=namespaces)
    
    for reason_description in reason_descriptions:
        lots_group = reason_description.xpath("ancestor::cac:ProcurementProjectLot[cbc:ID/@schemeName='LotsGroup']", namespaces=namespaces)[0]
        group_id = lots_group.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        results.append((group_id, reason_description.text))
    
    return results

def merge_unpublished_justification_description_lotsgroup_bt540(release_json, rationale_data):
    if not rationale_data:
        return

    if "withheldInformation" not in release_json:
        release_json["withheldInformation"] = []

    for group_id, rationale in rationale_data:
        withheld_item = next((item for item in release_json["withheldInformation"] if item.get("id") == f"awa-cri-des-group-{group_id}"), None)
        
        if withheld_item is None:
            withheld_item = {"id": f"awa-cri-des-group-{group_id}"}
            release_json["withheldInformation"].append(withheld_item)

        withheld_item["rationale"] = rationale