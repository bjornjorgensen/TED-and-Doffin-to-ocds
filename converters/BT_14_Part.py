# converters/BT_14_Part.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)

def parse_part_documents_restricted(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = {"tender": {"documents": []}}

    document_references = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']/cac:TenderingTerms/cac:CallForTendersDocumentReference", namespaces=namespaces)
    
    for doc_ref in document_references:
        doc_id = doc_ref.xpath("cbc:ID/text()", namespaces=namespaces)
        doc_type = doc_ref.xpath("cbc:DocumentType/text()", namespaces=namespaces)
        
        if doc_id and doc_type and doc_type[0].lower() == 'restricted-document':
            document_data = {
                "id": doc_id[0],
                "documentType": "biddingDocuments",
                "accessDetails": "Restricted."
            }
            result["tender"]["documents"].append(document_data)

    return result if result["tender"]["documents"] else None

def merge_part_documents_restricted(release_json, part_documents_restricted_data):
    if not part_documents_restricted_data:
        logger.warning("No part documents restricted data to merge")
        return

    existing_documents = release_json.setdefault("tender", {}).setdefault("documents", [])
    
    for new_document in part_documents_restricted_data["tender"]["documents"]:
        existing_document = next((doc for doc in existing_documents if doc["id"] == new_document["id"]), None)
        if existing_document:
            existing_document.update(new_document)
        else:
            existing_documents.append(new_document)

    logger.info(f"Merged part documents restricted data for {len(part_documents_restricted_data['tender']['documents'])} documents")