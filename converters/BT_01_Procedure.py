# converters/BT_01_Procedure.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)

def parse_procedure_legal_basis_id(xml_content):
    if isinstance(xml_content, str):
        xml_content = xml_content.encode('utf-8')
    root = etree.fromstring(xml_content)
    namespaces = {
    'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
    'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
    'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
    'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
    'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
    'efbc': 'http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1'
}

    legal_basis_elements = root.xpath(
        "//cac:ProcurementLegislationDocumentReference[not(cbc:ID='CrossBorderLaw' or cbc:ID='LocalLegalBasis')]/cbc:ID",
        namespaces=namespaces
    )

    if legal_basis_elements:
        legal_basis_id = legal_basis_elements[0].text
        return {
            "tender": {
                "legalBasis": {
                    "scheme": "ELI",
                    "id": legal_basis_id
                }
            }
        }
    else:
        logger.info("No Procedure Legal Basis ID found")
        return None

def parse_procedure_legal_basis_description(xml_content):
    if isinstance(xml_content, str):
        xml_content = xml_content.encode('utf-8')
    root = etree.fromstring(xml_content)
    namespaces = {
    'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
    'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
    'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
    'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
    'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
    'efbc': 'http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1'
}

    legal_basis_elements = root.xpath(
        "//cac:ProcurementLegislationDocumentReference[not(cbc:ID='CrossBorderLaw' or cbc:ID='LocalLegalBasis')]/cbc:DocumentDescription",
        namespaces=namespaces
    )

    if legal_basis_elements:
        legal_basis_description = legal_basis_elements[0].text
        return {
            "tender": {
                "legalBasis": {
                    "description": legal_basis_description
                }
            }
        }
    else:
        logger.info("No Procedure Legal Basis Description found")
        return None

def parse_procedure_legal_basis_noid(xml_content):
    if isinstance(xml_content, str):
        xml_content = xml_content.encode('utf-8')
    root = etree.fromstring(xml_content)
    namespaces = {
    'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
    'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
    'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
    'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
    'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
    'efbc': 'http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1'
}

    legal_basis_elements = root.xpath(
        "//cac:ProcurementLegislationDocumentReference[cbc:ID='LocalLegalBasis']/cbc:ID",
        namespaces=namespaces
    )

    if legal_basis_elements:
        legal_basis_id = legal_basis_elements[0].text
        return {
            "tender": {
                "legalBasis": {
                    "id": legal_basis_id
                }
            }
        }
    else:
        logger.info("No Procedure Legal Basis NoID found")
        return None

def parse_procedure_legal_basis_noid_description(xml_content):
    if isinstance(xml_content, str):
        xml_content = xml_content.encode('utf-8')
    root = etree.fromstring(xml_content)
    namespaces = {
    'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
    'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
    'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
    'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
    'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
    'efbc': 'http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1'
}

    legal_basis_elements = root.xpath(
        "//cac:ProcurementLegislationDocumentReference[cbc:ID='LocalLegalBasis']/cbc:DocumentDescription",
        namespaces=namespaces
    )

    if legal_basis_elements:
        legal_basis_description = legal_basis_elements[0].text
        return {
            "tender": {
                "legalBasis": {
                    "description": legal_basis_description
                }
            }
        }
    else:
        logger.info("No Procedure Legal Basis NoID Description found")
        return None

def parse_procedure_legal_basis_notice(xml_content):
    if isinstance(xml_content, str):
        xml_content = xml_content.encode('utf-8')
    root = etree.fromstring(xml_content)
    namespaces = {
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    regulatory_domain_elements = root.xpath("//cbc:RegulatoryDomain", namespaces=namespaces)

    if regulatory_domain_elements:
        regulatory_domain = regulatory_domain_elements[0].text
        return {
            "tender": {
                "legalBasis": {
                    "scheme": "CELEX",
                    "id": regulatory_domain
                }
            }
        }
    else:
        logger.info("No Procedure Legal Basis Notice found")
        return None

def merge_procedure_legal_basis(release_json, legal_basis_data):
    if not legal_basis_data:
        return

    tender = release_json.setdefault("tender", {})
    legal_basis = tender.setdefault("legalBasis", {})
    legal_basis.update(legal_basis_data["tender"]["legalBasis"])
    logger.info("Merged Procedure Legal Basis data")