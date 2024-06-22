# converters/BT_01.py
import lxml.etree as ET

def parse_legal_basis(xml_content):
    tender = {
        "legalBasis": {}
    }

    tree = ET.fromstring(xml_content)
    
    # BT-01(c)-Procedure: Procedure Legal Basis (ID)
    id_nodes = tree.xpath(
        "//*[local-name()='TenderingTerms']/*[local-name()='ProcurementLegislationDocumentReference'][not(*[local-name()='ID' and text()='CrossBorderLaw'] or *[local-name()='ID' and text()='LocalLegalBasis'])]/*[local-name()='ID']",
        namespaces={
            'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
            'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
        }
    )
    #print(f"BT-01(c) id_nodes: {[node.text for node in id_nodes]}")
    if id_nodes:
        tender["legalBasis"]["id"] = id_nodes[0].text
        tender["legalBasis"]["scheme"] = "ELI"
    
    # BT-01(d)-Procedure: Procedure Legal Basis (Description)
    desc_nodes = tree.xpath(
        "//*[local-name()='TenderingTerms']/*[local-name()='ProcurementLegislationDocumentReference'][not(*[local-name()='ID' and text()='CrossBorderLaw'] or *[local-name()='ID' and text()='LocalLegalBasis'])]/*[local-name()='DocumentDescription']",
        namespaces={
            'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
            'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
        }
    )
    #print(f"BT-01(d) desc_nodes: {[node.text for node in desc_nodes]}")
    if desc_nodes:
        tender["legalBasis"]["description"] = desc_nodes[0].text
    
    # BT-01(e)-Procedure: Procedure Legal Basis (NoID)
    local_id_nodes = tree.xpath(
        "//*[local-name()='TenderingTerms']/*[local-name()='ProcurementLegislationDocumentReference']/*[local-name()='ID' and text()='LocalLegalBasis']",
        namespaces={
            'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
            'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
        }
    )
    #print(f"BT-01(e) local_id_nodes: {[node.text for node in local_id_nodes]}")
    if local_id_nodes:
        tender["legalBasis"]["id"] = local_id_nodes[0].text
    
    # BT-01(f)-Procedure: Procedure Legal Basis (NoID Description)
    local_desc_nodes = tree.xpath(
        "//*[local-name()='TenderingTerms']/*[local-name()='ProcurementLegislationDocumentReference']/*[local-name()='ID' and text()='LocalLegalBasis']/following-sibling::*[local-name()='DocumentDescription']",
        namespaces={
            'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
            'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
        }
    )
    #print(f"BT-01(f) local_desc_nodes: {[node.text for node in local_desc_nodes]}")
    if local_desc_nodes:
        tender["legalBasis"]["description"] = local_desc_nodes[0].text

    # BT-01-notice: Procedure Legal Basis from RegulatoryDomain
    regulatory_domain_nodes = tree.xpath(
        "//*[local-name()='RegulatoryDomain']",
        namespaces={
            'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
        }
    )
    #print(f"BT-01-notice regulatory_domain_nodes: {[node.text for node in regulatory_domain_nodes]}")
    if regulatory_domain_nodes:
        tender["legalBasis"]["id"] = regulatory_domain_nodes[0].text
        tender["legalBasis"]["scheme"] = "CELEX"
    
    # Remove the 'legalBasis' key if it's empty
    if not tender["legalBasis"]:
        del tender["legalBasis"]
    
    return tender
