# converters/BT_09.py

from lxml import etree
import json

def parse_xml_to_json(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    cross_border_law = root.xpath("//cac:TenderingTerms/cac:ProcurementLegislationDocumentReference[cbc:ID/text()='CrossBorderLaw']/cbc:DocumentDescription", namespaces=namespaces)
    
    if cross_border_law:
        result = {
            "tender": {
                "crossBorderLaw": cross_border_law[0].text
            }
        }
        return json.dumps(result)
    else:
        return None