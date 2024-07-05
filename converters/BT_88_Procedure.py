# converters/BT_88_Procedure.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)

def parse_procedure_features(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    procedure_features = root.xpath('//cac:TenderingProcess/cbc:Description/text()', namespaces=namespaces)
    
    if procedure_features:
        return {"tender": {"procurementMethodDetails": procedure_features[0]}}
    else:
        logger.warning("No Procedure Features (BT-88) found in the XML")
        return None

def merge_procedure_features(release_json, procedure_features_data):
    if procedure_features_data and 'tender' in procedure_features_data:
        release_json.setdefault('tender', {})
        release_json['tender']['procurementMethodDetails'] = procedure_features_data['tender']['procurementMethodDetails']
        logger.info("Merged Procedure Features (BT-88) into the release JSON")
    else:
        logger.warning("No Procedure Features (BT-88) data to merge")