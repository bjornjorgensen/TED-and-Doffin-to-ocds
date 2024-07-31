# converters/BT_09_Procedure.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)

def parse_cross_border_law(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
    'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
    'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
    'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
    'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
    'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
    'efbc': 'http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1'
}

    xpath = "//cac:TenderingTerms/cac:ProcurementLegislationDocumentReference[cbc:ID/text()='CrossBorderLaw']/cbc:DocumentDescription/text()"
    cross_border_law = root.xpath(xpath, namespaces=namespaces)
    
    if cross_border_law:
        return {"tender": {"crossBorderLaw": cross_border_law[0]}}
    else:
        logger.warning("No Cross Border Law (BT-09) found in the XML")
        return None

def merge_cross_border_law(release_json, cross_border_law_data):
    if cross_border_law_data and 'tender' in cross_border_law_data:
        release_json.setdefault('tender', {})
        release_json['tender']['crossBorderLaw'] = cross_border_law_data['tender']['crossBorderLaw']
        logger.info("Merged Cross Border Law (BT-09) into the release JSON")
    else:
        logger.warning("No Cross Border Law (BT-09) data to merge")