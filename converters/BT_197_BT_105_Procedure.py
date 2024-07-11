# converters/BT_197_BT_105_Procedure.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)

NON_PUBLICATION_JUSTIFICATION = {
    "eo-int": {
        "description": "Commercial interests of an economic operator",
        "uri": "http://publications.europa.eu/resource/authority/non-publication-justification/eo-int"
    },
    "fair-comp": {
        "description": "Fair competition",
        "uri": "http://publications.europa.eu/resource/authority/non-publication-justification/fair-comp"
    },
    "law-enf": {
        "description": "Law enforcement",
        "uri": "http://publications.europa.eu/resource/authority/non-publication-justification/law-enf"
    },
    "oth-int": {
        "description": "Other public interest",
        "uri": "http://publications.europa.eu/resource/authority/non-publication-justification/oth-int"
    },
    "rd-ser": {
        "description": "Research and development (R&D) services",
        "uri": "http://publications.europa.eu/resource/authority/non-publication-justification/rd-ser"
    }
}

def parse_unpublished_justification_code_procedure_bt105(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
        'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
        'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
        'efbc': 'http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1'
    }

    xpath = "/*/cac:TenderingProcess/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='pro-typ']/cbc:ReasonCode"
    
    reason_code = root.xpath(xpath, namespaces=namespaces)
    
    if reason_code:
        return reason_code[0].text
    return None

def merge_unpublished_justification_code_procedure_bt105(release_json, justification_code):
    if not justification_code:
        return

    if "withheldInformation" not in release_json:
        release_json["withheldInformation"] = []

    withheld_item = next((item for item in release_json["withheldInformation"] if item.get("id", "").startswith("pro-typ-")), None)
    
    if withheld_item is None:
        withheld_item = {"id": "pro-typ-1"}
        release_json["withheldInformation"].append(withheld_item)

    if "rationaleClassifications" not in withheld_item:
        withheld_item["rationaleClassifications"] = []

    classification = {
        "scheme": "non-publication-justification",
        "id": justification_code
    }

    if justification_code in NON_PUBLICATION_JUSTIFICATION:
        classification["description"] = NON_PUBLICATION_JUSTIFICATION[justification_code]["description"]
        classification["uri"] = NON_PUBLICATION_JUSTIFICATION[justification_code]["uri"]

    withheld_item["rationaleClassifications"].append(classification)