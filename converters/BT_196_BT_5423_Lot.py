# converters/BT_196_BT_5423_Lot.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)

def parse_unpublished_justification_description_lot_bt5423(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
        'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
        'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
        'efbc': 'http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1'
    }

    xpath = "/*/cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']/cac:TenderingTerms/cac:AwardingTerms/cac:AwardingCriterion/cac:SubordinateAwardingCriterion/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:AwardCriterionParameter[efbc:ParameterCode/@listName='number-threshold']/efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='awa-cri-thr']/efbc:ReasonDescription"
    
    results = []
    reason_descriptions = root.xpath(xpath, namespaces=namespaces)
    
    for reason_description in reason_descriptions:
        lot = reason_description.xpath("ancestor::cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)[0]
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        results.append((lot_id, reason_description.text))
    
    return results

def merge_unpublished_justification_description_lot_bt5423(release_json, rationale_data):
    if not rationale_data:
        return

    if "withheldInformation" not in release_json:
        release_json["withheldInformation"] = []

    for lot_id, rationale in rationale_data:
        withheld_item = next((item for item in release_json["withheldInformation"] if item.get("id") == f"awa-cri-thr-{lot_id}"), None)
        
        if withheld_item is None:
            withheld_item = {"id": f"awa-cri-thr-{lot_id}"}
            release_json["withheldInformation"].append(withheld_item)

        withheld_item["rationale"] = rationale